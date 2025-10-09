<?php
require_once 'vendor/autoload.php';
session_start();

use Smarty\Smarty;
use Game\Driver;
use Game\Admin;
use Game\User;
use Game\Lap;

// 🔹 Smarty setup
$template = new Smarty();
$template->setTemplateDir('./templates');

// Routing via 'page' parameter
$page = $_GET['page'] ?? 'home';

switch ($page) {

    case 'home':
        // Actie voor het formulier
        $template->assign('form_action', 'index.php?page=home');
        $template->display('home.tpl');
        break;

    case 'addUser':
        $template->display('user-create.tpl');
        break;

    case 'userProfile':
        break;

    case 'lapTimeForm':
        if ($_SERVER['REQUEST_METHOD'] === 'POST') {
            if (!empty($_POST['sector1']) && !empty($_POST['sector2']) && !empty($_POST['sector3'])) {

                $sector1 = (float) $_POST['sector1'];
                $sector2 = (float) $_POST['sector2'];
                $sector3 = (float) $_POST['sector3'];
                $totalTime = $sector1 + $sector2 + $sector3;

                // Maak Lap object aan
                $lap = new Game\Lap(
                    driverId: 0,
                    sessionId: 0,
                    sector1: $sector1,
                    sector2: $sector2,
                    sector3: $sector3,
                    totalTime: $totalTime
                );

                // Zet de lap om naar array voordat we hem in de sessie stoppen
                $lapData = [
                    'sector1' => $lap->getSector1(),
                    'sector2' => $lap->getSector2(),
                    'sector3' => $lap->getSector3(),
                    'totalTime' => $lap->getTotalTime()
                ];

                if (!isset($_SESSION['laps'])) {
                    $_SESSION['laps'] = [];
                }
                $_SESSION['laps'][] = $lapData;

                $template->assign('lap', $lapData);
                $template->assign('laps', $_SESSION['laps']);
                $template->assign('confirmation', 'Ronde succesvol toegevoegd!');
            } else {
                $template->assign('error', '⚠️ Vul alle sectoren in!');
            }
        }

        $template->assign('form_action', 'index.php?page=lapTimeForm');
        $template->display('lap-form.tpl');
        break;

    case 'leaderboard':
        $template->assign('laps', $_SESSION['laps'] ?? []);
        $template->display('leaderboard.tpl');
        break;

    case 'deleteLap':
        if (isset($_POST['lapIndex']) && isset($_SESSION['laps'][$_POST['lapIndex']])) {
            unset($_SESSION['laps'][$_POST['lapIndex']]);
            $_SESSION['laps'] = array_values($_SESSION['laps']); // herindexeren
        }
        $template->assign('laps', $_SESSION['laps'] ?? []);
        $template->display('leaderboard.tpl');
        break;

    default:
        $template->display('home.tpl');
        break;
}
