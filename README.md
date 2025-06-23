# 🎨 Awesome Streamlit Themes

**Professional themes that transform your Streamlit apps from "obviously Streamlit" to "wow, that looks amazing!"**

No more cookie-cutter dashboards. No more identical-looking apps. Just beautiful, professional themes that make your Python apps shine! ✨

## 🙏 Built on Streamlit's Amazing Foundation

This project was inspired by [Thiago Teixeira](https://twitter.com/ThiagoTDotCom) (Streamlit co-founder) announcing [Streamlit's new theming capabilities](https://x.com/ThiagoTDotCom/status/1934679204320432283)! 🚀

The demo applications in this repo showcase the same UI elements from [Streamlit's official Anthropic-inspired example](https://github.com/streamlit/docs/tree/main/python/concept-source/theming-overview-anthropic-light-inspried) - this lets you see exactly how different themes transform the SAME interface. It's all about the visual transformation power of theming!

**What we've added:** 10 professional theme configurations that make Streamlit apps look incredible.  
**What Streamlit built:** The amazing theming system and demo interfaces that make this all possible.

## 🏥 [Healthcare Theme](healthcare/)

Perfect for medical dashboards and clinical applications

- Clinical blue design
- IBM Plex Sans typography
- Accessibility-focused
- Medical-grade professionalism

[📋 View Theme →](healthcare/)

---

## 💼 [Bootstrap Theme](bootstrap/)

Familiar styling every developer recognizes and loves

- Classic Bootstrap blue
- Inter typography
- Developer-friendly
- Instantly recognizable

[📋 View Theme →](bootstrap/)

---

## 🌙 [Dark Mode Developer](dark-mode/)

For late-night coding sessions and developer tools

- GitHub Dark colors
- JetBrains Mono code font
- Eye-friendly design
- VS Code vibes

[📋 View Theme →](dark-mode/)

---

## 📱 [Material Design](material-design/)

Google's systematic design language

- Material Blue palette
- Roboto typography
- Clean, familiar interface
- Android-inspired

[📋 View Theme →](material-design/)

---

## 🚀 [SaaS/Startup](saas-startup/)

Modern, growth-focused design for internal tools

- Purple accent colors
- DM Sans typography
- Startup energy
- Unicorn vibes

[📋 View Theme →](saas-startup/)

---

## 📰 [News/Editorial](editorial/)

Professional content-focused design

- Editorial red accents
- Serif typography
- High readability
- Publishing-grade

[📋 View Theme →](editorial/)

---

## 🎯 [Tailwind-Inspired](tailwind/)

Modern web standards everyone loves

- Clean blue design
- Inter typography
- Familiar patterns
- Web developer comfort

[📋 View Theme →](tailwind/)

---

## 💰 [Financial/Professional](financial/)

Corporate-grade design for serious business

- Deep navy colors
- Inter typography
- Enterprise credibility
- Boardroom-ready

[📋 View Theme →](financial/)

---

## 🌆 [Cyberpunk](cyberpunk/) _Fun Theme_

Retro-future synthwave aesthetics

- Hot pink and cyan
- Orbitron typography
- 80s vibes
- Pure awesome

[📋 View Theme →](cyberpunk/)

---

## 🧸 [Toddler-Friendly](toddler/) _Fun Theme_

Adorable design for educational apps

- Warm, soft colors
- Comic Neue typography
- Child-safe design
- Maximum cuteness

[📋 View Theme →](toddler/)

---

## 🚀 Quick Start

```bash
# Clone the entire repo to explore all themes
git clone https://github.com/jmedia65/awesome-streamlit-themes.git
cd awesome-streamlit-themes
pip install -r requirements.txt

# Choose any theme and see it in action (example: healthcare)
cd healthcare
streamlit run streamlit_app.py
```

**Love what you see?** Copy the theme to your project:

```bash
# Copy theme files to your Streamlit project
cp -r .streamlit/ /path/to/your/project/
cp -r static/ /path/to/your/project/
```

**That's it!** All fonts are included, no downloads needed. Just restart your Streamlit app and enjoy your beautiful new theme! ✨

## 💡 How It Works

Each theme uses Streamlit's new theming system with:

- `.streamlit/config.toml` - Theme configuration
- `static/` - Custom font files
- **One simple file** that transforms everything!

## 📖 Font Path Explanation

**Important:** Streamlit maps `app/static/` in config.toml to your project's `static/` folder. Always use `app/static/FontName.ttf` in your config even though fonts live in `static/FontName.ttf`.

## 📝 Attribution & Licensing

### Streamlit Demo Code

The Python demo applications are adapted from [Streamlit's official documentation examples](https://github.com/streamlit/docs), specifically the [Anthropic-inspired theming example](https://github.com/streamlit/docs/tree/main/python/concept-source/theming-overview-anthropic-light-inspried). These examples are used under the Apache 2.0 License to demonstrate how different themes transform the same interface.

### Google Fonts

All fonts used in these themes are from [Google Fonts](https://fonts.google.com/) and are licensed under the [SIL Open Font License (OFL)](https://openfontlicense.org/). Individual font license files are included in each theme's static folder.

### Theme Configurations

The theme configurations (`.streamlit/config.toml` files) in this repository are released under the MIT License - use them however you want!

## ⚠️ Disclaimer

This project is provided "as is" without warranty of any kind. The themes are for educational and development purposes. Users are responsible for ensuring proper licensing and attribution when using fonts and code in their projects.

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

## ⭐ Show Your Support

If these themes saved you hours of design work, give us a star! It helps other developers find these resources.

---

**Built with ❤️ for the Streamlit community**  
_Standing on the shoulders of the amazing Streamlit team_ 🚀
