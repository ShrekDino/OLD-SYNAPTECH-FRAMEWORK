using System.Text.Json;
using Terminal.Gui.Drawing;

namespace OpenMono.Tui.Rendering;

public class Theme
{
    public Color Background { get; init; }
    public Color Foreground { get; init; }
    public Color Muted { get; init; }
    public Color SyntaxKeyword { get; init; }
    public Color CodeBlockBg { get; init; }

    public ThemeScheme Normal => new(Background, Foreground);
    public ThemeScheme Dim => new(Background, Muted);
    public ThemeScheme Focus => new(Color.DarkGray, Foreground);

    public ThemeScheme GetSyntaxAttribute(TokenType token) => token switch
    {
        TokenType.Keyword => new ThemeScheme(CodeBlockBg, SyntaxKeyword),
        TokenType.String => new ThemeScheme(CodeBlockBg, Color.Yellow),
        TokenType.Comment => new ThemeScheme(CodeBlockBg, Color.Green),
        TokenType.Number => new ThemeScheme(CodeBlockBg, Color.Magenta),
        TokenType.Function => new ThemeScheme(CodeBlockBg, Color.Cyan),
        _ => new ThemeScheme(CodeBlockBg, Foreground),
    };

    public Theme MakeRoleScheme(Color foreground) => new()
    {
        Background = Background,
        Foreground = foreground,
        Muted = Muted,
        SyntaxKeyword = SyntaxKeyword,
        CodeBlockBg = CodeBlockBg,
    };
}

public class ThemeScheme
{
    public Color Background { get; }
    public Color Foreground { get; }

    public ThemeScheme(Color background, Color foreground)
    {
        Background = background;
        Foreground = foreground;
    }

    public void Deconstruct(out Color background, out Color foreground)
    {
        background = Background;
        foreground = Foreground;
    }
}

public static class ThemeManager
{
    private static Theme? _current;

    public static Theme Current => _current ?? Dark;

    public static Theme Dark => new()
    {
        Background = Color.Black,
        Foreground = Color.White,
        Muted = Color.DarkGray,
        SyntaxKeyword = Color.Cyan,
        CodeBlockBg = Color.Black,
    };

    public static Theme Light => new()
    {
        Background = Color.White,
        Foreground = Color.Black,
        Muted = Color.Gray,
        SyntaxKeyword = Color.Blue,
        CodeBlockBg = Color.White,
    };

    private static readonly Theme Monokai = new()
    {
        Background = Color.Parse("#272822"),
        Foreground = Color.Parse("#F8F8F2"),
        Muted = Color.Parse("#75715E"),
        SyntaxKeyword = Color.Parse("#F92672"),
        CodeBlockBg = Color.Parse("#272822"),
    };

    private static readonly Theme Solarized = new()
    {
        Background = Color.Parse("#002B36"),
        Foreground = Color.Parse("#839496"),
        Muted = Color.Parse("#586E75"),
        SyntaxKeyword = Color.Parse("#859900"),
        CodeBlockBg = Color.Parse("#002B36"),
    };

    public static void Load(string? configPath)
    {
        if (string.IsNullOrEmpty(configPath) || !File.Exists(configPath))
        {
            _current = Dark;
            return;
        }

        try
        {
            var json = File.ReadAllText(configPath);
            using var doc = JsonDocument.Parse(json);
            var root = doc.RootElement;

            var themeName = "dark";
            if (root.TryGetProperty("theme", out var themeProp))
                themeName = themeProp.GetString() ?? "dark";

            _current = ResolveBuiltIn(themeName);

            if (root.TryGetProperty("customTheme", out var custom))
            {
                var bg = custom.TryGetProperty("background", out var bgProp)
                    ? Color.Parse(bgProp.GetString() ?? "#000000")
                    : _current.Background;
                var fg = custom.TryGetProperty("foreground", out var fgProp)
                    ? Color.Parse(fgProp.GetString() ?? "#FFFFFF")
                    : _current.Foreground;
                var syntaxKw = custom.TryGetProperty("syntax", out var syntax)
                    && syntax.TryGetProperty("keyword", out var kwProp)
                    ? Color.Parse(kwProp.GetString() ?? "#00FFFF")
                    : _current.SyntaxKeyword;

                _current = new Theme
                {
                    Background = bg,
                    Foreground = fg,
                    Muted = _current.Muted,
                    SyntaxKeyword = syntaxKw,
                    CodeBlockBg = _current.CodeBlockBg,
                };
            }
        }
        catch
        {
            _current = Dark;
        }
    }

    public static Theme ResolveBuiltIn(string name) => (name.ToLowerInvariant()) switch
    {
        "light" => Light,
        "monokai" => Monokai,
        "solarized" => Solarized,
        _ => Dark,
    };
}
