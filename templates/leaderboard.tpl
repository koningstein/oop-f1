{extends file='layout.tpl'}

{block name='content'}
    <div class="container mt-5" style="max-width: 700px;">
        <div class="card shadow" style="border: 2px solid var(--redbull-blue);">
            <div class="card-body" style="background-color: var(--redbull-white); color: var(--redbull-blue);">
                <h2 class="card-title mb-4" style="color: var(--redbull-blue);">Leaderboard</h2>

                {if isset($laps) && $laps|@count > 0}
                    <table class="table table-striped">
                        <thead>
                        <tr>
                            <th>#</th>
                            <th>Sector 1</th>
                            <th>Sector 2</th>
                            <th>Sector 3</th>
                            <th>Totaal Tijd</th>
                            <th>Actie</th>
                        </tr>
                        </thead>
                        <tbody>
                        {foreach $laps as $index => $lap}
                            {assign var="total" value=$lap.sector1 + $lap.sector2 + $lap.sector3}
                            <tr>
                                <td>{$index+1}</td>
                                <td>{$lap.sector1}</td>
                                <td>{$lap.sector2}</td>
                                <td>{$lap.sector3}</td>
                                <td>{$total}</td>
                                <td>
                                    <form method="post" action="index.php?page=deleteLap" style="display:inline;">
                                        <input type="hidden" name="lapIndex" value="{$index}">
                                        <button type="submit" class="btn btn-danger btn-sm">Verwijder</button>
                                    </form>
                                </td>
                            </tr>
                        {/foreach}
                        </tbody>
                    </table>
                {else}
                    <p>Er zijn nog geen rondes toegevoegd.</p>
                {/if}

                <a href="index.php?page=lapTimeForm" class="btn btn-primary mt-3">Nieuwe ronde toevoegen</a>
            </div>
        </div>
    </div>
{/block}
