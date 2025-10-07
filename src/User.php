<?php

namespace Game;

abstract class User
{
  protected $studentNumber;
  protected $name;
  protected $class;

  public function __construct($name, $class = null, $studentNumber = null)
  {
    $this->name = $name;
    $this->class = $class;
    $this->studentNumber = $studentNumber;
  }

  public function getName()
  {
    return $this->name;
  }

  public function getClass()
  {
    return $this->class;
  }

  public function getStudentNumber()
  {
    return $this->studentNumber;
  }

  public function setName($name)
  {
    $this->name = $name;
  }

  public function setClass($class)
  {
    $this->class = $class;
  }

  public function setStudentNumber($studentNumber)
  {
    $this->studentNumber = $studentNumber;
  }

  abstract public function getRole();
}