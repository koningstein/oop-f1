{extends file='layout.tpl'}
{block name='content'}
    <div class="container mt-5" style="max-width: 500px;">
        <div class="card shadow" style="border: 2px solid var(--redbull-blue);">
            <div class="card-body" style="background-color: var(--redbull-white); color: var(--redbull-blue);">
                <h2 class="card-title mb-4" style="color: var(--redbull-blue);">Mijn Profiel</h2>
                <form method="post" action="user_profile.php">
                    <div class="mb-3">
                        <label for="name" class="form-label" style="color: var(--redbull-blue);">Naam:</label>
                        <input type="text" id="name" name="name" class="form-control" value="{$user.name}" required>
                    </div>
                    <div class="mb-3">
                        <label for="class" class="form-label" style="color: var(--redbull-blue);">Klas:</label>
                        <input type="text" id="class" name="class" class="form-control" value="{$user.class}" required>
                    </div>
                    <div class="mb-3">
                        <label for="studentNumber" class="form-label" style="color: var(--redbull-blue);">Studentnummer:</label>
                        <input type="text" id="studentNumber" name="studentNumber" class="form-control" value="{$user.studentNumber}" required>
                    </div>
                    <button type="submit" class="btn w-100 fw-bold"
                            style="background-color: var(--redbull-red); color: var(--redbull-white); border: none;">
                        Opslaan
                    </button>
                </form>
            </div>
        </div>
    </div>
{/block}
