<?php
namespace Game;

class Lap
{
    private float $sector1;
    private float $sector2;
    private float $sector3;
    private float $totalTime;

    public function __construct(float $sector1, float $sector2, float $sector3)
    {
        $this->sector1 = $sector1;
        $this->sector2 = $sector2;
        $this->sector3 = $sector3;
        $this->totalTime = $sector1 + $sector2 + $sector3;
    }

    // Getters
    public function getSector1(): float
    {
        return $this->sector1;
    }

    public function getSector2(): float
    {
        return $this->sector2;
    }

    public function getSector3(): float
    {
        return $this->sector3;
    }

    public function getTotalTime(): float
    {
        return $this->totalTime;
    }

    // Optioneel: handig als je data in 1 array wil stoppen
    public function toArray(): array
    {
        return [
            'sector1' => $this->sector1,
            'sector2' => $this->sector2,
            'sector3' => $this->sector3,
            'total' => $this->totalTime
        ];
    }
}
