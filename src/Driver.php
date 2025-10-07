<?php

namespace Game;

require_once 'User.php';

class Driver extends User
{
  public function __construct($studentNumber, $name, $class)
  {
    parent::__construct($name, $class, $studentNumber);
  }

  public function getRole()
  {
    return "Driver";
  }
}