import numpy as np

MU_DIM = 64
MU_DTYPE = np.float64
MMAP_PATH = '/dev/shm/dak_state.mmap'
CHECKPOINT_PATH = '/tmp/dak_checkpoint.mmap'
PERTURB_PATH = '/tmp/dak_perturb.json'

LEARNING_RATE = 0.05
MOMENTUM = 0.0
MU_INIT_SCALE = 0.1
GRADIENT_CLIP_NORM = 10.0

N_SENSORS = 15
SIGMA2_LIK = 1.0
SIGMA2_PRIOR = 1.0
W_INIT_SCALE = 0.1

DRIFT_DURATION = 5.0
SAMPLING_DURATION = 2.0
TICK_INTERVAL = 0.1

KB = 1.0
EPSILON = 0.8
SZILARD_THRESHOLD = 1.0

SENSOR_WINDOW = 100
MU_HISTORY_SIZE = 1000

MI_THRESHOLD = 1.0

LOG_PATH = '/tmp/dak_ledger.jsonl'

# Episodic memory
MEMORY_ENABLED = True
MEMORY_PERSIST_DIR = '/tmp/erebus_memory'
CHROMA_COLLECTION_NAME = 'erebus_episodes'
COMPRESSION_INTERVAL = 1000

# Safety
SAFETY_ENABLED = True
SAFETY_AUDIT_LOG = '/tmp/dak_audit.jsonl'

# Sandbox execution
SANDBOX_ENABLED = True
SANDBOX_TIMEOUT = 30.0
SANDBOX_MAX_MEM_MB = 100
SANDBOX_MAX_DISK_MB = 50
SANDBOX_WORK_DIR = '/tmp/erebus_workspace'

# Network access
NETWORK_ALLOWLIST = []
NETWORK_RATE_LIMIT = 10

# USF transformer runtime flags
USF_ENABLED = False
