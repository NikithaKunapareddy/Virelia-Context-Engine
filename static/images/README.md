# Static Images Directory

This directory contains static images used in the web interface.

## File Structure

- `favicon.ico` - Browser favicon
- `logo.png` - Application logo
- `bg-pattern.png` - Background pattern
- `icons/` - UI icons and illustrations

## Usage

Images are served statically by Flask and can be referenced in templates using:

```html
<img src="{{ url_for('static', filename='images/logo.png') }}" alt="Logo">
```

## Supported Formats

- PNG (recommended for logos and icons)
- JPG (for photographs)
- SVG (for scalable graphics)
- ICO (for favicons)

## Guidelines

- Optimize images for web use
- Use descriptive filenames
- Include alt text for accessibility
- Consider responsive image needs
