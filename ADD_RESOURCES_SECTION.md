# Adding a New Resources Section

This guide outlines the process for adding new sections to the Resources pages.

## Process Overview

1. **Create the template file** (`templates/static_pages/resources_<section-slug>.html`)
2. **Add URL route** in `lrgnetwork/urls.py`
3. **Add to Resources index** table of contents
4. **Optimize images** (if any are >500KB)
5. **Test the page**

## Step-by-Step Instructions

### 1. Create Template File

Create a new file: `templates/static_pages/resources_<section-slug>.html`

Use this template structure:

```django
{% extends "base.html" %}
{% load static %}
{% load compress %}

{% block title %}<Section Title> - Resources - LRG Network{% endblock %}

{% block extra_css %}
{% compress css %}
<link rel="stylesheet" href="{% static 'resources/styles.css' %}">
{% endcompress %}
{% endblock %}

{% block content %}
<div class="container-xl py-3">
  <div class="row mb-4">
    <div class="col-12 text-center">
      <h1 class="mb-4"><Section Title></h1>
    </div>
  </div>

  <div class="row">
    <div class="col-12 col-lg-10 mx-auto">
      <div class="resource-content">
        <!-- Your content here -->

        <!-- Images: alternate R/L/R/L positioning -->
        <div class="resource-image-wrapper float-lg-end mb-4 mb-lg-3">
          <img src="{% static 'resources/images/filename.jpg' %}" alt="Descriptive alt text" class="img-fluid resource-image">
          <p class="resource-image-caption text-center">Photo: Game Name</p>
        </div>

        <div class="resource-image-wrapper float-lg-start mb-4 mb-lg-3">
          <img src="{% static 'resources/images/filename2.jpg' %}" alt="Descriptive alt text" class="img-fluid resource-image">
          <p class="resource-image-caption text-center">Photo: Game Name</p>
        </div>

        <!-- More content -->
      </div>
    </div>
  </div>

  <div class="row mt-5">
    <div class="col-12 text-center">
      <a href="{% url 'resources' %}" class="btn btn-outline-secondary">Back to Resources</a>
    </div>
  </div>
</div>
{% endblock %}
```

**Image Positioning Rules:**
- Alternate between `float-lg-end` (right) and `float-lg-start` (left)
- Pattern: R, L, R, L, etc.
- Always include `mb-4 mb-lg-3` classes
- Use `resource-image-wrapper` class
- Captions: use `resource-image-caption text-center` class

### 2. Add URL Route

In `lrgnetwork/urls.py`, add a new path:

```python
path(
    "resources/<section-slug>/",
    TemplateView.as_view(template_name="static_pages/resources_<section-slug>.html"),
    name="resources_<section_slug>",
),
```

**Example:**
```python
path(
    "resources/budgets/",
    TemplateView.as_view(template_name="static_pages/resources_budgets.html"),
    name="resources_budgets",
),
```

### 3. Add to Resources Index

In `templates/static_pages/resources_index.html`, add a new entry to the table of contents:

```django
<li class="mb-2">
  <a href="{% url 'resources_<section_slug>' %}" class="text-decoration-none">
    <strong><Section Title></strong>
  </a>
  <p class="small text-muted mb-0 mt-1">Brief description</p>
</li>
```

### 4. Add Images

1. Upload images to `static/resources/images/`
2. Use descriptive filenames (lowercase, hyphens): `my_game_name.jpg`
3. If images are >500KB, optimize them:

```bash
make optimize-images
```

Or manually:
```bash
cd static/resources/images
sips -s formatOptions 85 filename.jpg
sips -Z 1200 filename.jpg
```

### 5. Content Guidelines

- **Headers**: Use `<h3 class="h5 mb-2">` for section headers
- **Lists**: Use `<ul>` with `<li>` items
- **Paragraphs**: Use `<div class="mb-4">` wrapper for paragraphs
- **Lead text**: Use `<p class="lead">` for emphasized paragraphs
- **Links**: Use standard Bootstrap button classes for external links

## Quick Checklist

- [ ] Template file created with correct structure
- [ ] URL route added to `urls.py`
- [ ] Added to Resources index table of contents
- [ ] Images optimized (if needed)
- [ ] Images positioned alternately (R/L/R/L)
- [ ] Image captions included with "Photo: Game Name" format
- [ ] "Back to Resources" button included
- [ ] Page tested in browser

## Providing Content

You can provide content in any format, and I'll:
1. Structure it properly with the template format
2. Insert images at appropriate points
3. Format headers, lists, and paragraphs
4. Alternate image positioning (R/L/R/L)
5. Add captions to images
6. Set up all the routing

Just give me:
- Section title
- Content (text)
- Image filenames and where they should go (or I can decide)
- Game names for captions
- Any external links (YouTube, etc.)
