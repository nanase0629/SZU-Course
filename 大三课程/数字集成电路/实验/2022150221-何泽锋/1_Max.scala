import chisel3._

class Max3 extends Module {
  val io = IO(new Bundle {
    val in1 = Input(UInt(16.W))
    val in2 = Input(UInt(16.W))
    val in3 = Input(UInt(16.W))
    val out = Output(UInt(16.W))
  })

  io.out := 0.U

  when (io.in1 > io.in2) {
    io.out := io.in1
  }.otherwise {
    io.out := io.in2
  }

  when (io.out < io.in3) {
    io.out := io.in3
  }
}
