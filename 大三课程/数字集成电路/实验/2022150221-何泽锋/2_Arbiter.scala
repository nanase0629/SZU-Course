import chisel3._

class Arbiter extends Module {
  val io = IO(new Bundle {
    // mod1
    val mod1_valid = Input(Bool())
    val mod1_ready = Output(Bool())
    val mod1_data  = Input(UInt(16.W))
    // mod2
    val mod2_valid = Output(Bool())
    val mod2_ready = Input(Bool())
    val mod2_data  = Output(UInt(16.W))
    // mod3
    val mod3_valid = Output(Bool())
    val mod3_ready = Input(Bool())
    val mod3_data  = Output(UInt(16.W))
  })

  io.mod2_valid := false.B
  io.mod3_valid := false.B
  io.mod1_ready := false.B
  io.mod2_data := 0.U
  io.mod3_data := 0.U

  when (io.mod1_valid) {
    when (io.mod2_ready && !io.mod3_ready) {
      io.mod2_valid := true.B
      io.mod2_data := io.mod1_data
      io.mod1_ready := true.B
    }.elsewhen (!io.mod2_ready && io.mod3_ready) {
      io.mod3_valid := true.B
      io.mod3_data := io.mod1_data
      io.mod1_ready := true.B
    }.elsewhen (io.mod2_ready && io.mod3_ready) {
      io.mod2_valid := true.B
      io.mod2_data := io.mod1_data
      io.mod1_ready := true.B
    }
  }.otherwise {
    io.mod2_valid := false.B
    io.mod3_valid := false.B
  }
}
