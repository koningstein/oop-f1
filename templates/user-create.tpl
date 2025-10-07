{extends file='layout.tpl'}
{block name='content'}
    <div class="container mt-5" style="max-width: 500px;">
        <div class="card shadow" style="border: 2px solid var(--redbull-white);">
            <div class="card-body" style="background-color: var(--redbull-white); color: var(--redbull-blue); ">
                <h2 class="card-title mb-4" style="color: var(--redbull-blue);">Nieuw Coureur-profiel</h2>
                <form method="post" action="driver_create.php">
                    <div class="mb-3">
                        <label for="name" class="form-label" style="color: var(--redbull-blue);">Naam:</label>
                        <input type="text" id="name" name="name" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="class" class="form-label" style="color: var(--redbull-blue);">Klas:</label>
                        <input type="text" id="class" name="class" class="form-control" required>
                    </div>
                    <div class="mb-3">
                        <label for="studentNumber" class="form-label" style="color: var(--redbull-blue);">Studentnummer:</label>
                        <input type="text" id="studentNumber" name="studentNumber" class="form-control" required>
                    </div>
                    <button type="submit" class="btn w-100 fw-bold"
                            style="background-color: var(--redbull-blue); color: var(--redbull-white); border: none;">
                        Aanmaken
                    </button>
                </form>
            </div>
        </div>
    </div>
{/block}
