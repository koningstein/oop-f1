<?php

namespace Game;

require_once 'User.php';

class Driver extends User
{
  public function __construct($email, $name, $class)
  {
    parent::__construct($name, $class, $email);
  }

  public function getRole()
  {
    return "Driver";
  }
}