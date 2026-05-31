using System.Text.Json;
using Terminal.Gui.Input;

namespace OpenMono.Tui.Keybindings;

public enum TuiAction
{
    Pause,
    ToggleSidebar,
    Help,
    Clear,
    Compact,
    Undo,
    Retry,
    Status,
    Stats,
    Think,
    Plan,
    Export,
    Resume,
    Quit,
    Cancel,
    ScrollUp,
    ScrollDown,
    PageUp,
    PageDown,
}

public class KeybindingManager
{
    private readonly Dictionary<TuiAction, Key> _defaults = new()
    {
        [TuiAction.Pause] = Key.P.WithCtrl,
        [TuiAction.ToggleSidebar] = Key.S.WithCtrl,
        [TuiAction.Help] = Key.F1,
        [TuiAction.Clear] = Key.L.WithCtrl,
        [TuiAction.Compact] = Key.M.WithCtrl,
        [TuiAction.Undo] = Key.Z.WithCtrl,
        [TuiAction.Retry] = Key.R.WithCtrl,
        [TuiAction.Status] = Key.I.WithCtrl,
        [TuiAction.Stats] = Key.T.WithCtrl,
        [TuiAction.Export] = Key.E.WithCtrl,
        [TuiAction.Resume] = Key.D.WithCtrl,
        [TuiAction.Quit] = Key.Q.WithCtrl,
        [TuiAction.ScrollUp] = Key.CursorUp,
        [TuiAction.ScrollDown] = Key.CursorDown,
        [TuiAction.PageUp] = Key.PageUp,
        [TuiAction.PageDown] = Key.PageDown,
    };

    private readonly Dictionary<TuiAction, Key> _bindings;

    private static readonly Dictionary<TuiAction, string> KeyHints = new()
    {
        [TuiAction.Pause] = "^P",
        [TuiAction.ToggleSidebar] = "^S",
        [TuiAction.Help] = "F1",
        [TuiAction.Clear] = "^L",
        [TuiAction.Compact] = "^M",
        [TuiAction.Undo] = "^Z",
        [TuiAction.Retry] = "^R",
        [TuiAction.Status] = "^I",
        [TuiAction.Stats] = "^T",
        [TuiAction.Export] = "^E",
        [TuiAction.Resume] = "^D",
        [TuiAction.Quit] = "^Q",
        [TuiAction.ScrollUp] = "\u2191",
        [TuiAction.ScrollDown] = "\u2193",
        [TuiAction.PageUp] = "PgUp",
        [TuiAction.PageDown] = "PgDn",
    };

    public KeybindingManager(string? configPath = null)
    {
        _bindings = new Dictionary<TuiAction, Key>(_defaults);

        if (!string.IsNullOrEmpty(configPath) && File.Exists(configPath))
            LoadOverrides(configPath);
    }

    public Key? GetKey(TuiAction action) =>
        _bindings.TryGetValue(action, out var key) ? key : null;

    public TuiAction? Resolve(Key key)
    {
        foreach (var (action, binding) in _bindings)
        {
            if (key == binding)
                return action;
        }
        return null;
    }

    public string GetHint(TuiAction action) =>
        KeyHints.TryGetValue(action, out var hint) ? hint : string.Empty;

    private void LoadOverrides(string configPath)
    {
        try
        {
            var json = File.ReadAllText(configPath);
            using var doc = JsonDocument.Parse(json);
            foreach (var prop in doc.RootElement.EnumerateObject())
            {
                if (Enum.TryParse<TuiAction>(prop.Name, out var action))
                {
                    var keyStr = prop.Value.GetString();
                    if (keyStr is not null && TryParseKey(keyStr, out var key))
                        _bindings[action] = key;
                }
            }
        }
        catch
        {
            _bindings.Clear();
            foreach (var kv in _defaults)
                _bindings[kv.Key] = kv.Value;
        }
    }

    private static bool TryParseKey(string keyStr, out Key key)
    {
        key = Key.Empty;
        try
        {
            var parts = keyStr.Split('+');
            var baseKey = Key.Empty;
            var hasCtrl = false;
            var hasShift = false;
            var hasAlt = false;

            foreach (var part in parts)
            {
                var trimmed = part.Trim();
                if (trimmed.Equals("Ctrl", StringComparison.OrdinalIgnoreCase))
                    hasCtrl = true;
                else if (trimmed.Equals("Shift", StringComparison.OrdinalIgnoreCase))
                    hasShift = true;
                else if (trimmed.Equals("Alt", StringComparison.OrdinalIgnoreCase))
                    hasAlt = true;
                else if (trimmed.StartsWith("F", StringComparison.OrdinalIgnoreCase) &&
                         int.TryParse(trimmed[1..], out var fNum))
                {
                    baseKey = fNum switch
                    {
                        1 => Key.F1, 2 => Key.F2, 3 => Key.F3, 4 => Key.F4,
                        5 => Key.F5, 6 => Key.F6, 7 => Key.F7, 8 => Key.F8,
                        9 => Key.F9, 10 => Key.F10, 11 => Key.F11, 12 => Key.F12,
                        _ => baseKey
                    };
                }
                else if (trimmed.Equals("Escape", StringComparison.OrdinalIgnoreCase) ||
                         trimmed.Equals("Esc", StringComparison.OrdinalIgnoreCase))
                {
                    hasCtrl = false;
                    hasShift = false;
                    hasAlt = false;
                    baseKey = Key.Esc;
                }
                else if (trimmed.Length == 1 && char.IsAsciiLetterUpper(trimmed[0]))
                {
                    baseKey = trimmed[0] switch
                    {
                        'A' => Key.A, 'B' => Key.B, 'C' => Key.C, 'D' => Key.D,
                        'E' => Key.E, 'F' => Key.F, 'G' => Key.G, 'H' => Key.H,
                        'I' => Key.I, 'J' => Key.J, 'K' => Key.K, 'L' => Key.L,
                        'M' => Key.M, 'N' => Key.N, 'O' => Key.O, 'P' => Key.P,
                        'Q' => Key.Q, 'R' => Key.R, 'S' => Key.S, 'T' => Key.T,
                        'U' => Key.U, 'V' => Key.V, 'W' => Key.W, 'X' => Key.X,
                        'Y' => Key.Y, 'Z' => Key.Z,
                        _ => baseKey
                    };
                }
                else return false;
            }

            if (hasCtrl) baseKey = baseKey.WithCtrl;
            if (hasShift) baseKey = baseKey.WithShift;
            if (hasAlt) baseKey = baseKey.WithAlt;

            key = baseKey;
            return true;
        }
        catch
        {
            return false;
        }
    }
}
