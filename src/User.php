<?php

namespace Game;

abstract class User
{
  protected $name;
  protected $class;
  protected $email;

  public function __construct($name, $class = null, $email = null)
  {
    $this->name = $name;
    $this->class = $class;
    $this->email = $email;
  }

  public function getName()
  {
    return $this->name;
  }

  public function getClass()
  {
    return $this->class;
  }

  public function getEmail()
  {
    return $this->email;
  }

  public function setName($name)
  {
    $this->name = $name;
  }

  public function setClass($class)
  {
    $this->class = $class;
  }

  public function setEmail($email)
  {
    $this->email = $email;
  }

  abstract public function getRole();
}