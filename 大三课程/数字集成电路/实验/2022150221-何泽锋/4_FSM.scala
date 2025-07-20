import chisel3._

class GradLife extends Module {
  // ¶¨ÒåIO¶Ë¿Ú
  val io = IO(new Bundle {
    val coffee = Input(Bool())
    val idea = Input(Bool())
    val pressure = Input(Bool())
    val state = Output(UInt(2.W))
  })

  val idle :: coding :: writing :: grad :: Nil = Enum(4)
  val stateReg = RegInit(idle)

  switch(stateReg) {
    is(idle) {
      when(io.coffee) {
        stateReg := coding
      }.elsewhen(io.idea) {
        stateReg := idle
      }.elsewhen(io.pressure) {
        stateReg := writing
      }.otherwise {
        stateReg := idle
      }
    }
    is(coding) {
      when(io.coffee) {
        stateReg := coding
      }.elsewhen(io.idea) {
        stateReg := writing
      }.elsewhen(io.pressure) {
        stateReg := writing
      }.otherwise {
        stateReg := idle
      }
    }
    is(writing) {
      when(io.coffee) {
        stateReg := writing
      }.elsewhen(io.idea) {
        stateReg := writing
      }.elsewhen(io.pressure) {
        stateReg := grad
      }.otherwise {
        stateReg := idle
      }
    }
    is(grad) {
      stateReg := idle 
    }
  }

  io.state := stateReg
}
