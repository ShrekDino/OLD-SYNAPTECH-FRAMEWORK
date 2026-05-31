import json
import math
import os
import time
import uuid
from contextlib import asynccontextmanager

import numpy as np
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse

from flywire_lsm.config import (
    CHAR_TO_IDX,
    IDX_TO_CHAR,
    N_A,
    N_NEURONS,
    STEPS_PER_TOKEN,
    TEMPERATURE,
    VOCAB_SIZE,
)
from flywire_lsm.logging import get_logger
from flywire_lsm.simulation import ReservoirSimulation

_LOG = get_logger()


@asynccontextmanager
async def lifespan(app):
    global sim, NODE_POSITIONS, TOP_EDGES

    sim = ReservoirSimulation()

    train_text = (
        "The FlyWire Connectome is a two-region hierarchical liquid state machine. "
        "It has five hundred neurons split into two modules. Module A handles fast "
        "sensory input. Module B provides slow deep memory retention. "
        "Hello there! How are you today? I am doing well thank you for asking. "
        "What is your name? My name is FlyWire. I am a brain simulation. "
        "Can you help me with this task? Yes I can help you with it. "
        "What is the answer to the question? The answer is forty two. "
        "Where is the library located? It is on the left side of the building. "
        "The quick brown fox jumps over the lazy dog near the river. "
        "She sells sea shells by the sea shore. The shells she sells are sea shells. "
        "The rain in Spain falls mainly on the plain. That is a fact. "
        "Machine learning is a fascinating field of study. Neural networks can learn "
        "complex patterns from data. Reservoir computing uses fixed random connections "
        "with trained readout weights. This is a powerful technique for temporal data. "
        "The weather today is sunny and warm. Tomorrow it will rain. Please remember "
        "to bring an umbrella with you. The temperature will be seventy five degrees. "
        "I like to read books about science and technology. My favorite subjects are "
        "physics chemistry and biology. Learning new things is always exciting and fun. "
        "What is the capital of France? The capital of France is Paris. "
        "What color is the sky? The sky is blue during the day and black at night. "
        "Tell me a story about a brave knight. The brave knight fought the dragon "
        "and saved the kingdom from destruction. Everyone was happy and grateful. "
        "Please turn on the lights. The room is too dark for reading and writing. "
        "Good morning! Did you sleep well? Yes I slept very well thank you. "
        "What would you like to eat for dinner? I would like to have pasta and salad. "
        "The cat sat on the mat. The dog ran after the ball. The bird flew in the sky. "
        "One two three four five six seven eight nine ten. These are the first ten "
        "numbers. Eleven twelve thirteen fourteen fifteen. Counting is easy and fun. "
        "Artificial intelligence is transforming the world in amazing ways. "
        "Self driving cars can navigate roads without human help. "
        "Voice assistants can answer questions and play music for you. "
        "Robots can build cars and explore distant planets like Mars. "
        "Hello world welcome to the FlyWire Connectome simulation. "
        "This system learns to predict the next character in a sequence. "
        "It uses a liquid state machine with two specialized brain regions. "
        "The sensory region registers input quickly. The memory region stores "
        "information over time. Together they form a powerful computing system. "
        "Can you teach me something new today? Yes I can teach you about reservoirs. "
        "A reservoir computer has three parts. The input layer the reservoir layer "
        "and the readout layer. Only the readout layer is trained. "
        "The reservoir is fixed and random. This makes training fast and simple. "
        "Why is the sky blue? It is blue because of Rayleigh scattering. "
        "Light from the sun scatters in the atmosphere. Blue light scatters more "
        "than red light. That is why the sky appears blue to our eyes. "
        "What is the meaning of life? That is a deep question. Some say it is "
        "forty two. Others say it is about learning and growing. "
        "Please write a poem about a tree. A tree stands tall and proud and free. "
        "Its branches reach up to the sky. Its roots go deep into the earth. "
        "It gives us shade and fruit and air. The tree is a friend to all. "
        "Where do stars come from? Stars are born in clouds of gas and dust. "
        "Gravity pulls the gas together until it becomes hot and dense. "
        "Then nuclear fusion begins and a star is born. Stars shine for billions "
        "of years before they fade away. That is the life cycle of a star. "
        "Tell me a joke. What do you call a fish with no eyes? A fsh. "
        "That is a silly joke but it makes me smile. "
        "The end of the training text is here. Thank you for reading it. "
        "I hope this helps the LSM learn language patterns better."
    )
    acc = sim.train_readout(train_text, num_passes=2)
    _LOG.info("[STARTUP] Initial training accuracy: %.4f", acc)

    hist = _load_history()
    if not hist.get("learning_history"):
        hist["learning_history"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text_trained": "Default Baseline Dataset",
            "accuracy": float(acc),
        })
        _save_history(hist)

    NODE_POSITIONS, TOP_EDGES = _compute_topology()
    _LOG.info("[STARTUP] Topology computed: %d nodes, %d edges",
              len(NODE_POSITIONS), len(TOP_EDGES))

    yield


app = FastAPI(title="FlyWire Connectome Live Viewer", lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sim: ReservoirSimulation | None = None
NODE_POSITIONS: list[dict] = []
TOP_EDGES: list[dict] = []


def _compute_topology() -> tuple[list[dict], list[dict]]:
    h = sim.hlayer

    def _to_dense(g):
        W = np.zeros((g.n, g.n_pre))
        for post in range(g.n):
            for idx in range(g.colptr[post], g.colptr[post + 1]):
                W[post, g.rows[idx]] = g.data[idx]
        return W

    W_AA = _to_dense(h.graph_AA)
    W_BB = _to_dense(h.graph_BB)
    W_AB = _to_dense(h.graph_AB)
    W_BA = _to_dense(h.graph_BA)

    W_full = np.zeros((N_NEURONS, N_NEURONS))
    W_full[:N_A, :N_A] = W_AA
    W_full[N_A:, N_A:] = W_BB
    W_full[N_A:, :N_A] = W_AB
    W_full[:N_A, N_A:] = W_BA

    non_zero_mask = W_full != 0
    non_zero_abs = np.abs(W_full[non_zero_mask])
    if len(non_zero_abs) > 0:
        thresh = np.percentile(non_zero_abs, 98)
        posts, pres = np.where(np.abs(W_full) >= thresh)
        edge_list = []
        for post, pre in zip(posts, pres):
            w = W_full[post, pre]
            if w != 0:
                edge_list.append({
                    "source": int(pre),
                    "target": int(post),
                    "weight": float(w),
                })
    else:
        edge_list = []

    golden_angle = math.pi * (3.0 - math.sqrt(5.0))
    positions = []
    for i in range(200):
        side = -1 if i < 100 else 1
        t = 2.0 * math.pi * (i % 100) / 100.0
        x = side * (55 + 42 * math.cos(t))
        y = -28 + 30 * math.sin(t) + 8 * math.cos(t * 2)
        z = 72 + 28 * math.cos(t) + 12 * math.sin(t * 3)
        positions.append({
            "id": i, "x": x, "y": y, "z": z,
            "region": "Sensory Neuropil",
        })
    for i in range(300):
        theta = golden_angle * i
        phi = math.acos(1.0 - 2.0 * (i + 0.5) / 300.0)
        x = 82 * math.sin(phi) * math.cos(theta)
        y = 12 + 62 * math.cos(phi)
        z = -8 + 52 * math.sin(phi) * math.sin(theta)
        positions.append({
            "id": 200 + i, "x": x, "y": y, "z": z,
            "region": "Central Complex",
        })

    _LOG.info("[TOPOLOGY] %d nodes, %d top-edges (top 2%%)", len(positions), len(edge_list))
    return positions, edge_list


HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "history.json")


def _load_history() -> dict:
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception as e:
            _LOG.error("[HISTORY] Error reading history file: %s", str(e))
    return {"chats": [], "learning_history": []}


def _save_history(data: dict) -> None:
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        _LOG.error("[HISTORY] Error writing history file: %s", str(e))


@app.get("/topology")
async def get_topology():
    return {"nodes": NODE_POSITIONS, "edges": TOP_EDGES}


@app.post("/train")
async def train_endpoint(req: Request):
    body = await req.json()
    text = body.get("text", "")
    warm_start = body.get("warm_start", False)
    num_passes = body.get("num_passes", 2)
    if not text:
        return JSONResponse({"error": "Empty training text"}, status_code=400)
    acc = sim.train_readout(text, warm_start=warm_start, cumulative=True, num_passes=num_passes)

    try:
        hist = _load_history()
        hist["learning_history"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text_trained": text[:150] + "..." if len(text) > 150 else text,
            "accuracy": float(acc),
        })
        _save_history(hist)
    except Exception as e:
        _LOG.error("[HISTORY] Failed to save train run: %s", str(e))

    return {"accuracy": float(acc)}


@app.post("/chat")
async def chat_endpoint(req: Request):
    body = await req.json()
    prompt = body.get("prompt", "")
    temperature = body.get("temperature", TEMPERATURE)
    if not prompt:
        return JSONResponse({"error": "Empty prompt"}, status_code=400)
    if not sim.readout.trained:
        return JSONResponse({"error": "Readout not trained"}, status_code=400)

    def event_stream():
        sim.hlayer.reset()
        generated: list[str] = []

        for char in prompt:
            if char not in CHAR_TO_IDX:
                continue
            I_inj = sim.encoder.encode(char)
            for _ in range(STEPS_PER_TOKEN):
                sim.hlayer.step(I_inj, log=False)
            state = sim.hlayer.get_state()
            logits = sim.readout.predict(state)
            pred_idx = int(np.argmax(logits))
            pred_char = IDX_TO_CHAR.get(pred_idx, "?")
            generated.append(pred_char)
            yield f"data: {json.dumps({'token': pred_char, 'activations': state.tolist()})}\n\n"

        for _ in range(25):
            last_pred = generated[-1]
            if last_pred not in CHAR_TO_IDX:
                break
            I_inj = sim.encoder.encode(last_pred)
            for _ in range(STEPS_PER_TOKEN):
                sim.hlayer.step(I_inj, log=False)
            state = sim.hlayer.get_state()
            logits = sim.readout.predict(state)

            if temperature > 0:
                scaled = logits / temperature
                scaled -= scaled.max()
                probs = np.exp(scaled)
                probs /= probs.sum()
                next_idx = int(sim.rng.choice(VOCAB_SIZE, p=probs))
            else:
                next_idx = int(np.argmax(logits))
            next_char = IDX_TO_CHAR.get(next_idx, "?")
            generated.append(next_char)
            yield f"data: {json.dumps({'token': next_char, 'activations': state.tolist()})}\n\n"

        try:
            full_response = "".join(generated)
            hist = _load_history()
            hist["chats"].append({
                "id": str(uuid.uuid4()),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "prompt": prompt,
                "response": full_response,
                "accuracy_at_time": float(sim.latest_accuracy),
            })
            _save_history(hist)
        except Exception as e:
            _LOG.error("[HISTORY] Failed to save chat to history: %s", str(e))

        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/history")
async def get_history():
    return _load_history()


@app.post("/history/clear")
async def clear_history():
    data = {"chats": [], "learning_history": []}
    if sim is not None:
        data["learning_history"].append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "text_trained": "Default Baseline Dataset",
            "accuracy": float(sim.latest_accuracy),
        })
    _save_history(data)
    return {"status": "success"}


FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")


@app.get("/")
async def index():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))


def main() -> None:
    import uvicorn
    uvicorn.run("flywire_lsm.server:app", host="0.0.0.0", port=8000, reload=False)


if __name__ == "__main__":
    main()
