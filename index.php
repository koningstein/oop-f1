<?php
require_once 'vendor/autoload.php';
session_start();

use Smarty\Smarty;
use Game\Driver;
use Game\Admin;
use Game\User;

// 🔹 Smarty setup
$template = new Smarty();
$template->setTemplateDir('./templates');

// Routing via 'page' parameter
$page = $_GET['page'] ?? 'home';

switch ($page) {

    case 'home':
        // Als het formulier is ingediend
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            if (!empty($_POST['sector1']) && !empty($_POST['sector2']) &&
                !empty($_POST['sector3']) && !empty($_POST['laptime'])) {

                $sector1 = (float) $_POST['sector1'];
                $sector2 = (float) $_POST['sector2'];
                $sector3 = (float) $_POST['sector3'];
                $laptime = (float) $_POST['laptime'];

                // Hier kan later database logica komen
                // Bijvoorbeeld:
                // $stmt = $pdo->prepare("INSERT INTO laps (sector1, sector2, sector3, laptime) VALUES (?, ?, ?, ?)");
                // $stmt->execute([$sector1, $sector2, $sector3, $laptime]);

                // Bevestiging en data aan Smarty geven
                $template->assign('confirmation', 'Ronde succesvol toegevoegd!');
                $template->assign('sector1', $sector1);
                $template->assign('sector2', $sector2);
                $template->assign('sector3', $sector3);
                $template->assign('laptime', $laptime);
            } else {
                $template->assign('error', '⚠️ Vul alle velden in!');
            }
        }

        // Actie voor het formulier
        $template->assign('form_action', 'index.php?page=home');
        $template->display('home.tpl');
        break;
  case 'addUser':
    $template->display('user-create.tpl');

    break;
  case 'userProfile':

    break;



    // 🔸 Later kun je hier meer pagina’s toevoegen:
    // case 'leaderboard':
    //     // Haal rondes op uit database of sessie
    //     $template->assign('laps', $laps);
    //     $template->display('leaderboard.tpl');
    //     break;

    // case 'about':
    //     $template->display('about.tpl');
    //     break;

    default:
        $template->display('home.tpl');
        break;
}
