<!doctype html>
<html lang="en" class="h-100" data-bs-theme="light">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Red Bull Racing Leaderboard</title>

    <link href="./templates/css/bootstrap.min.css" rel="stylesheet">

    <style>
        /* 🌈 Red Bull kleuren */
        :root {
            --redbull-blue: #000B8D;
            --redbull-red: #E21B4D;
            --redbull-yellow: #FFD300;
            --redbull-white: #F4EBEE;
        }

        body {
            background-color: #ffffff;
            color: #000;
            font-family: 'Poppins', sans-serif;
        }

        /* 🔹 Navbar */
        .navbar {
            background-color: var(--redbull-blue) !important;
            box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
        }
        .navbar-brand {
            color: var(--redbull-yellow) !important;
            font-weight: 700;
            text-transform: uppercase;
        }
        .nav-link {
            color: #fff !important;
            font-weight: 500;
            transition: 0.2s;
        }
        .nav-link:hover, .nav-link.active {
            color: var(--redbull-red) !important;
        }

        /* 🔹 Container content */
        main .container {
            background: #fff;
            border-radius: 15px;
            padding: 2rem;
            margin-top: 100px;
            box-shadow: 0 0 20px rgba(30, 65, 255, 0.15);
        }

        h1, h2, h3, h4, h5 {
            color: var(--redbull-blue);
            font-weight: 700;
        }

        .btn-redbull {
            background-color: var(--redbull-red);
            color: #fff;
            font-weight: bold;
            border: none;
            transition: 0.2s;
        }
        .btn-redbull:hover {
            background-color: #ff0900;
        }

        /* 🔹 Footer */
        footer {
            background-color: var(--redbull-blue);
            color: #fff;
        }
        footer span {
            color: var(--redbull-white);
        }

        /* 🔹 Lijst items */
        .list-group-item {
            border-radius: 8px;
            margin-bottom: 0.5rem;
        }
    </style>
</head>

<body class="d-flex flex-column h-100">

<header>
    <!-- Fixed navbar -->
    <nav class="navbar navbar-expand-md navbar-dark fixed-top">
        <div class="container-fluid">
            <!-- Logo + Merknaam -->
            <a class="navbar-brand d-flex align-items-center" href="index.php?page=home">
                <img src="./templates/img/red-bull-logo.png" alt="Red Bull Logo" height="50" class="me-2">
            </a>

            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarCollapse"
                    aria-controls="navbarCollapse" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>

            <div class="collapse navbar-collapse" id="navbarCollapse">
                <ul class="navbar-nav me-auto mb-2 mb-md-0">
                    <li class="nav-item">
                        <a class="nav-link {if $page == 'leaderboard'}active{/if}" href="index.php?page=leaderboard">Leaderboard</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {if $page == 'addUser'}active{/if}" href="index.php?page=addUser">Maak Gebruiker aan</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {if $page == 'addlap'}active{/if}" href="index.php?page=lapTimeForm">Voeg ronde toe</a>
                    </li>

                </ul>
            </div>
        </div>
    </nav>
</header>

<!-- Begin page content -->
<main class="flex-shrink-0">
    <div class="container">
        {block name="content"}{/block}
    </div>
</main>

<!-- Footer -->
<footer class="footer mt-auto py-3 text-center">
    <div class="container">
        <span>© 2025 <strong>Red Bull Racing Leaderboard</strong> — Engineered for Speed 🏁</span>
    </div>
</footer>

<script defer src="./templates/js/bootstrap.bundle.min.js"></script>
</body>
</html>
