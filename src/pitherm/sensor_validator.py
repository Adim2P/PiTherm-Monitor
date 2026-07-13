from dataclasses import dataclass

from src.pitherm.config import (
    TEMP_MIN_VALID,
    TEMP_MAX_VALID,
    HUMIDITY_MIN_VALID,
    HUMIDITY_MAX_VALID,
    MAX_TEMP_JUMP,
    MAX_HUMIDITY_JUMP
)

@dataclass
class ValidationResult:
    is_valid: bool
    reason: str | None = None

class SensorValidator:
    def __init__(self):
        self._last_valid_temperature: float | None = None
        self._last_valid_humidity: float | None = None
    
    def validate(
            self,
            temperature: float,
            humidity: float
    ) -> ValidationResult:
        
        if not (
            TEMP_MIN_VALID
            <= temperature
            <= TEMP_MAX_VALID
        ):
            return ValidationResult(
                False,
                (
                    f"Temperature ({temperature:.2f}°C) "
                    f"is outside the valid range "
                    f"({TEMP_MIN_VALID:.2f}°C - "
                    f"{TEMP_MAX_VALID:.2f}°C)."
                )
            )
        
        if not (
            HUMIDITY_MIN_VALID
            <= humidity
            <= HUMIDITY_MAX_VALID
        ):
            return ValidationResult(
                False,
                (
                    f"Humidity ({humidity:.2f}%) "
                    f"is outside the valid range "
                    f"({HUMIDITY_MIN_VALID:.2f}% - "
                    f"{HUMIDITY_MAX_VALID:.2f}%)."
                )
            )
        
        if self._last_valid_temperature is not None:
            temp_jump = abs(
                temperature - self._last_valid_temperature
            )

            if temp_jump > MAX_TEMP_JUMP:
                return ValidationResult(
                    False,
                    (
                        f"Temperature jumped "
                        f"{temp_jump:.2f}°C "
                        f"({self._last_valid_temperature:.2f}°C -> "
                        f"{temperature:.2f}°C."
                    )
                )
        
        if self._last_valid_humidity is not None:
            humidity_jump = abs(
                humidity - self._last_valid_humidity
            )

            if humidity_jump > MAX_HUMIDITY_JUMP:
                return ValidationResult(
                    False,
                    (
                        f"Humidity jumped "
                        f"{humidity_jump:.2f}% "
                        f"({self._last_valid_humidity:.2f}% -> "
                        f"{humidity:.2f}%."
                    )
                )
        
        self._last_valid_temperature = temperature
        self._last_valid_humidity = humidity

        return ValidationResult(
            is_valid = True
        )
