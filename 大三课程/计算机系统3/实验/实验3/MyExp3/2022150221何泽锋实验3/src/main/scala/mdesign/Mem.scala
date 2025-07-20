package mydesign

import chisel3._

class Mem extends Module {
	val io = IO(new Bundle {
		val rdAddr = Input(UInt(5.W))
		val rdData = Output(UInt(32.W))
		val wrAddr = Input(UInt(5.W))
		val wrData = Input(UInt(32.W))
		val wrEna  = Input(UInt(1.W))
	})

	val mem = SyncReadMem(32, UInt(32.W))

	io.rdData := mem.read(io.rdAddr)

	when(io.wrEna === 1.U) {
		mem.write(io.wrAddr, io.wrData)
	}
}
