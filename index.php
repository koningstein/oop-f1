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

if (isset($_SESSION['user'])) {
  $template->assign('user', $_SESSION['user']);
}
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
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {
      $name = $_POST['name'] ?? '';
      $class = $_POST['class'] ?? '';
      $email = $_POST['email'] ?? '';

      // Create Driver object
      $driver = new Driver($name, $class, $email);
      $_SESSION['driver'] = $driver;

      $_SESSION['user'] = [
        'name' => $name,
        'class' => $class,
        'email' => $email
      ];

      header('Location: index.php?page=user-created');
      exit;
    }
    $template->display('user-create.tpl');
    break;
  case 'user-created':
    $template->display('user-created.tpl');
    break;

    case 'leaderboard':
        $template->assign('laps', $_SESSION['laps'] ?? []);
        $template->display('leaderboard.tpl');
        break;
  case 'userProfile':
    if ($_SERVER['REQUEST_METHOD'] === 'POST') {

      $name = trim($_POST['name'] ?? '');
      $class = trim($_POST['class'] ?? '');
      $email = trim($_POST['email'] ?? '');

      // Update session user
      $_SESSION['user']['name'] = $name;
      $_SESSION['user']['class'] = $class;
      $_SESSION['user']['email'] = $email;


      header('Location: index.php?page=userProfile');
      exit;
    }
    $template->display('user-profile.tpl');
    break;
    case 'logout':
        session_destroy();
        $template->display('logout.tpl');
        exit;
        break;
    case 'deleteLap':
        if (isset($_POST['lapIndex']) && isset($_SESSION['laps'][$_POST['lapIndex']])) {
            unset($_SESSION['laps'][$_POST['lapIndex']]);
            $_SESSION['laps'] = array_values($_SESSION['laps']); // herindexeren
        }
        $template->assign('laps', $_SESSION['laps'] ?? []);
        $template->display('leaderboard.tpl');
        break;



  // 🔸 Later kun je hier meer pagina’s toevoegen:
    // case 'about':
    //     $template->display('about.tpl');
    //     break;

    default:
        $template->display('home.tpl');
        break;
}
