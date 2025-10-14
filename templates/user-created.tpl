{extends file='layout.tpl'}
{block name='content'}
    <div class="container mt-5">
        <div class="alert alert-success text-center" role="alert">
            <h2 class="mb-4">User successfully created!</h2>
            <div class="d-flex justify-content-center gap-3">
                <a href="index.php?page=home" class="btn btn-primary">Home Page</a>
                <a href="index.php?page=addLaptime" class="btn btn-success">Add Laptimes</a>
            </div>
        </div>
    </div>
{/block}
