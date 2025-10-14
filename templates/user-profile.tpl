{extends file='layout.tpl'}
{block name='content'}
    <style>
        :root {
            --redbull-blue: #00205b;
            --redbull-red: #e2231a;
            --redbull-yellow: #ffd100;
            --redbull-white: #fff;
        }
        .rb-card {
            border: 3px solid var(--redbull-blue);
            border-radius: 18px;
            box-shadow: 0 6px 24px rgba(0,32,91,0.12);
            background: linear-gradient(135deg, var(--redbull-white) 80%, #fffbe6 100%);
        }

        .rb-title {
            color: var(--redbull-blue);
            font-weight: 900;
            letter-spacing: 1px;
        }
        .rb-label {
            color: var(--redbull-blue);
            font-weight: 600;
        }
        .rb-input {
            border: 2px solid var(--redbull-blue);
            border-radius: 8px;
            background: var(--redbull-white);
            color: var(--redbull-blue);
        }
        .rb-input:focus {
            border-color: var(--redbull-red);
            box-shadow: 0 0 0 2px var(--redbull-yellow);
        }
        .rb-btn {
            background: linear-gradient(90deg, var(--redbull-red) 60%, var(--redbull-yellow) 100%);
            color: var(--redbull-white);
            font-weight: bold;
            border: none;
            border-radius: 8px;
            transition: background 0.2s;
        }
        .rb-btn:hover {
            background: linear-gradient(90deg, var(--redbull-yellow) 60%, var(--redbull-red) 100%);
            color: var(--redbull-blue);
        }
        .rb-logo {
            display: block;
            margin: 0 auto 18px auto;
            width: 80px;
        }
    </style>
    <div class="container mt-5" style="max-width: 500px;">
        <div class="card rb-card">
            <div class="card-body">
                <img src="templates/img/red-bull-logo.png" alt="Red Bull Logo" class="rb-logo">
                <h2 class="card-title mb-4 rb-title">Mijn Profiel</h2>
                <form method="post" action="index.php?page=userProfile">
                    <div class="mb-3">
                        <label for="name" class="form-label rb-label">Naam:</label>
                        <input type="text" id="name" name="name" class="form-control rb-input" value="{$user.name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="class" class="form-label rb-label">Klas:</label>
                        <input type="text" id="class" name="class" class="form-control rb-input" value="{$user.class}" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label rb-label">Email:</label>
                        <input type="text" id="email" name="email" class="form-control rb-input" value="{$user.email}" required>
                    </div>
                    <button type="submit" class="btn w-100 fw-bold rb-btn">
                        Opslaan
                    </button>
                </form>
                <div class="d-grid mt-3">
                    <a href="index.php?page=logout" class="btn rb-btn">Uitloggen</a>
                </div>
            </div>
        </div>
    </div>
{/block}
