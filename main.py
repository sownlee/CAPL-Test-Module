// SignalWatcher.can - Giám sát timeout signal
variables
{
  msTimer tVehicleSpeed;     // Timer cho signal VehicleSpeed
  int gSpeedLastValue = -1;
  int gSpeedTimeout = 0;     // 0 = OK, 1 = Timeout
}

on start
{
  write("SignalWatcher CAPL started - Monitoring VehicleSpeed timeout");
  tVehicleSpeed.setTimer(600);  // 600ms > 500ms → đủ để phát hiện timeout
  gSpeedTimeout = 0;
}

on signal VehicleSpeed
{
  gSpeedLastValue = this.value;
  tVehicleSpeed.setTimer(600);   // Reset timer mỗi khi nhận signal
  if (gSpeedTimeout == 1)
  {
    write("VehicleSpeed signal RECOVERED at %.2f km/h", this.value);
    gSpeedTimeout = 0;
  }
}

on timer tVehicleSpeed
{
  if (gSpeedTimeout == 0)
  {
    write("ERROR: VehicleSpeed TIMEOUT! Last value: %d", gSpeedLastValue);
    gSpeedTimeout = 1;
  }
  // Timer tự động restart để tiếp tục giám sát
  this.setTimer(600);
}

// Hàm để Python đọc kết quả
int GetSpeedTimeoutStatus()
{
  return gSpeedTimeout;
}