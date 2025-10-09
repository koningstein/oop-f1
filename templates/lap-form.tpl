{extends file='layout.tpl'}

{block name='content'}
    <div class="container mt-5" style="max-width: 500px;">
        <div class="card shadow" style="border: 2px solid var(--redbull-blue);">
            <div class="card-body" style="background-color: var(--redbull-white); color: var(--redbull-blue);">
                <h2 class="card-title mb-4" style="color: var(--redbull-blue);">Voer een ronde in</h2>
                <form method="post" id="lapForm">
                    <div class="mb-3">
                        <label for="sector1" class="form-label" style="color: var(--redbull-blue);">Sector 1:</label>
                        <input type="number" step="0.001" id="sector1" name="sector1" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="sector2" class="form-label" style="color: var(--redbull-blue);">Sector 2:</label>
                        <input type="number" step="0.001" id="sector2" name="sector2" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="sector3" class="form-label" style="color: var(--redbull-blue);">Sector 3:</label>
                        <input type="number" step="0.001" id="sector3" name="sector3" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="totalTime" class="form-label" style="color: var(--redbull-blue);">Totale tijd:</label>
                        <input type="number" step="0.001" id="totalTime" name="totalTime" class="form-control" required>
                    </div>
                    <button type="submit" class="btn w-100 fw-bold" style="background-color: var(--redbull-blue); color: var(--redbull-white); border: none;">
                        Voeg ronde toe
                    </button>
                </form>
            </div>
        </div>
    </div>

    {* Modal voor bevestiging *}
    <div class="modal fade" id="confirmationModal" tabindex="-1" aria-hidden="true">
        <div class="modal-dialog modal-dialog-centered">
            <div class="modal-content" style="border: 2px solid var(--redbull-blue);">
                <div class="modal-header" style="background-color: var(--redbull-blue); color: var(--redbull-white);">
                    <h5 class="modal-title">Ronde toegevoegd!</h5>
                </div>
                <div class="modal-body">
                    <p><strong>Sector 1:</strong> <span id="modalSector1"></span>s</p>
                    <p><strong>Sector 2:</strong> <span id="modalSector2"></span>s</p>
                    <p><strong>Sector 3:</strong> <span id="modalSector3"></span>s</p>
                    <hr>
                    <p><strong>Totaal:</strong> <span id="modalTotal"></span>s</p>
                </div>
                <div class="modal-footer">
                    <a href="index.php?page=leaderboard" class="btn" style="background-color: var(--redbull-red); color: var(--redbull-white);">Verder</a>
                </div>
            </div>
        </div>
    </div>

{literal}
    <script>
        document.getElementById('lapForm').addEventListener('submit', function(e){
            e.preventDefault();

            const sector1 = document.getElementById('sector1').value;
            const sector2 = document.getElementById('sector2').value;
            const sector3 = document.getElementById('sector3').value;
            const totalTime = document.getElementById('totalTime').value;

            // Vul modal met waarden
            document.getElementById('modalSector1').textContent = sector1;
            document.getElementById('modalSector2').textContent = sector2;
            document.getElementById('modalSector3').textContent = sector3;
            document.getElementById('modalTotal').textContent = totalTime;

            // Verstuur data via fetch naar PHP om in session op te slaan
            fetch('index.php?page=lapTimeForm', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: 'sector1=' + sector1 + '&sector2=' + sector2 + '&sector3=' + sector3 + '&totalTime=' + totalTime
            }).then(response => response.text())
                .then(() => {
                    const modal = new bootstrap.Modal(document.getElementById('confirmationModal'));
                    modal.show();
                });
        });
    </script>
{/literal}

{/block}
