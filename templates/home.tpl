{extends file='layout.tpl'}

{block name='content'}
    <div class="container text-center mt-5">
        <h1 class="display-4 fw-bold" style="color: #e70a0a;">Welkom bij het Red Bull Racing Leaderboard!</h1>

        <p class="lead mt-3 text-secondary" style="max-width: 700px; margin: 0 auto;">
            Dit platform is ontworpen om de prestaties van coureurs vast te leggen en te vergelijken.
            Volg de rondetijden, verbeter je prestaties en zie wie de snelste is op het circuit!
        </p>

        <hr class="my-4" style="border: 2px solid #FFD700; width: 60%; margin: 1rem auto;">

        <h3 class="fw-bold" style="color: #DA291C;">Wat kun je doen?</h3>
        <ul class="list-group text-start mt-3 shadow-sm" style="max-width: 700px; margin: 0 auto; border-radius: 10px;">
            <li class="list-group-item border-0 border-bottom" style="background-color: #f8f9fa;">
                🟡 <strong>1.</strong> Bekijk het <span style="color:#1E41FF;">Leaderboard</span> om te zien wie de snelste ronde heeft gereden.
            </li>
            <li class="list-group-item border-0 border-bottom" style="background-color: #f8f9fa;">
                🔵 <strong>2.</strong> Analyseer wie constant snel is in de races.
            </li>
            <li class="list-group-item border-0" style="background-color: #f8f9fa;">
                🔴 <strong>3.</strong> Word zelf de snelste — just like <strong>Red Bull Racing</strong>! 💨
            </li>
        </ul>

        <p class="mt-4 text-muted">
            Klaar om te starten? Bekijk het leaderboard hieronder.
        </p>

        <a class="btn btn-redbull btn-lg px-4 py-2" href="index.php?page=leaderboard" role="button">
            Bekijk het Leaderboard
        </a>
    </div>
{/block}
