import chisel3._

class MyShiftRegister extends Module {
    val io = IO(new Bundle {
    val in  = Input(Bool())
    val out = Output(UInt(4.W))
  })

    val state = RegInit(UInt(4.W), 1.U)

    state := Cat(io.in, state(3, 1))

    io.out := state
}
