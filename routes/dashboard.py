<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard</title>

    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>

<body>

<nav class="navbar">
    <div class="logo">
        URL Shortener
    </div>

    <ul class="menu">
        <li><a href="/">Home</a></li>
        <li><a href="/dashboard">Dashboard</a></li>
    </ul>
</nav>

<section class="hero">

    <h1>Dashboard</h1>

    <div class="features">

        <div class="card">
            <h2>Total Links</h2>
            <p>{{ total_links }}</p>
        </div>

        <div class="card">
            <h2>Total Clicks</h2>
            <p>{{ total_clicks }}</p>
        </div>

    </div>

    <h2>Your Links</h2>

    <table>

        <tr>
            <th>Original URL</th>
            <th>Short URL</th>
            <th>Clicks</th>
            <th>Actions</th>
        </tr>

        {% for url in urls %}

        <tr>

            <td>{{ url.original_url }}</td>

            <td>
                <a href="{{ request.host_url }}{{ url.short_code }}" target="_blank">
                    {{ request.host_url }}{{ url.short_code }}
                </a>
            </td>

            <td>{{ url.clicks }}</td>

            <td style="display:flex;gap:8px;flex-wrap:wrap;">

                <button
                    type="button"
                    onclick="copyLink('{{ request.host_url }}{{ url.short_code }}')">
                    📋 Copy
                </button>

                <a href="{{ request.host_url }}{{ url.short_code }}" target="_blank">
                    <button type="button">
                        🔗 Open
                    </button>
                </a>

                <form
                    action="{{ url_for('links.delete_link', url_id=url.id) }}"
                    method="POST"
                    onsubmit="return confirm('Delete this link?');">

                    <button type="submit">
                        🗑 Delete
                    </button>

                </form>

            </td>

        </tr>

        {% endfor %}

    </table>

</section>

<script src="{{ url_for('static', filename='js/script.js') }}"></script>

</body>
</html>
