# 💙 Bootstrap-Inspired Theme

**The popular web framework that millions of developers know - now for Streamlit!**

Instantly familiar, professionally trusted, and widely recognized. This theme brings Bootstrap's signature aesthetic to your Streamlit apps, making them feel like real web applications! 🌐✨

![Bootstrap Theme](bootstrap.png)

## 🔥 What Makes This Theme Special

Bootstrap is one of the most widely used CSS frameworks - and now your Streamlit apps can capture that same trusted aesthetic:

**🔵 Bootstrap's Primary Blue** (#0d6efd) - Familiar to many web developers  
**📱 System-Like Feel** - Clean, familiar, professional web app aesthetic  
**⚙️ Bootstrap Border Radius** (0.375rem) - Bootstrap's default border-radius value  
**📊 Bootstrap Gray Scale** - Bootstrap's defined gray palette (#f8f9fa, #e9ecef)  
**🎯 Modern Typography** - Inter font for clean web application feel  
**🧩 Component-Ready** - Designed to feel like Bootstrap-built interfaces

## 🎯 Perfect For

- **Internal business tools** and dashboards
- **Admin panels** and management interfaces
- **Data analysis platforms** that need credibility
- **Customer support tools** and CRM systems
- **Developer tools** and monitoring dashboards
- **Applications needing** familiar web design patterns
- **Enterprise applications** that require professional appearance
- **Educational platforms** and learning management systems

## 🚀 Quick Start

```bash
# Clone the entire repo to see all themes
git clone https://github.com/jmedia65/awesome-streamlit-themes.git
cd awesome-streamlit-themes

# Install dependencies
pip install -r requirements.txt

# Navigate to bootstrap theme and see it in action
cd bootstrap
streamlit run streamlit_app.py
```

**Love what you see?** Copy the theme to your project:

```bash
# Copy theme files to your Streamlit project
cp -r .streamlit/ /path/to/your/project/
cp -r static/ /path/to/your/project/
```

## 🛠️ Fonts Used

_All fonts are already included in the `static/` folder - no downloads needed!_

### Inter (Modern Web Typography)

- **Perfect for:** Clean, web-optimized typography for modern interfaces
- **Used for:** Body text, headings, interface elements
- **Source:** [Google Fonts - Inter](https://fonts.google.com/specimen/Inter)

### JetBrains Mono (Developer-Friendly Monospace)

- **Perfect for:** Clean, modern monospace preferred by many developers
- **Used for:** Code snippets, monospace text
- **Source:** [Google Fonts - JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono)

## 📁 Installation Steps

1. **Clone and explore** the theme first (see Quick Start above)
2. **Copy theme files** to your own Streamlit project:
   ```
   your-project/
   ├── .streamlit/
   │   └── config.toml          # ← Copy this!
   ├── static/                  # ← Copy this entire folder!
   │   ├── Inter_18pt-Regular.ttf
   │   ├── Inter_18pt-Medium.ttf
   │   ├── Inter_18pt-SemiBold.ttf
   │   ├── Inter_18pt-Bold.ttf
   │   ├── JetBrainsMono-Regular.ttf
   │   └── JetBrainsMono-Medium.ttf
   └── your_app.py
   ```
3. **Restart your Streamlit app** and enjoy the Bootstrap-inspired design!

## 🎨 Theme Configuration

The implementation happens in `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#0d6efd"              # Bootstrap 5's primary blue
backgroundColor = "#ffffff"           # Pure white - Bootstrap's foundation
secondaryBackgroundColor = "#f8f9fa"  # Bootstrap's gray-50
textColor = "#212529"                 # Bootstrap's body text color
linkColor = "#0d6efd"                 # Bootstrap primary for links
borderColor = "#dee2e6"               # Bootstrap's border-color
```

## 🏆 The Developer Recognition Factor

Many developers will recognize this aesthetic and think: "This looks like a professional web application." It has the visual credibility of Bootstrap's design system - systematic, clean, and trustworthy.

This theme bridges the gap between "obviously Streamlit" and "looks like a real web app" by using familiar design patterns from one of the web's most popular frameworks.

## 💡 Why Bootstrap-Inspired Design Works

✅ **Familiar Patterns** - Users trust interfaces with recognizable design patterns  
✅ **Professional Polish** - Systematic design that feels intentional  
✅ **Developer Familiarity** - Many web developers have experience with Bootstrap  
✅ **Enterprise Appropriate** - Conservative, professional choice for business applications  
✅ **Responsive Principles** - Based on mobile-first design thinking  
✅ **Well-Documented** - Based on Bootstrap's publicly available design system

## 🎯 Pro Tips

- **Perfect for client presentations** - familiar patterns build trust
- **Great for internal tools** that need quick user adoption
- **Ideal for data dashboards** that business users will access
- **Excellent for prototypes** that need to feel production-ready

---

**Built with 💙 for developers who appreciate familiar, reliable design**  
_Bringing Bootstrap's trusted aesthetic to the Streamlit world_ 🚀
