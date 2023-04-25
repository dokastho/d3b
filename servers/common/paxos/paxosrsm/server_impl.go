package paxosrsm

import (
	// "fmt"
	"d3b/paxos"
	"sync"
	"time"
)

//
// additions to PaxosRSM state
//
type PaxosRSMImpl struct {
	set_sync sync.Mutex
	seq      int
}

//
// initialize rsm.impl.*
//
func (rsm *PaxosRSM) InitRSMImpl() {
	rsm.impl.seq = 0
}

//
// application invokes AddOp to submit a new operation to the replicated log
// AddOp returns only once value v has been decided for some Paxos instance
//
// a call to AddOp() will block until the specified operation becomes the
// decided value for one of the Paxos instances
//
func (rsm *PaxosRSM) AddOp(v interface{}) {
	rsm.impl.set_sync.Lock()
	defer rsm.impl.set_sync.Unlock()

	// use max for seq, that way if the local paxos instance has fallen behind
	// it will catch up
	for {
		rsm.impl.seq += 1
		rsm.px.Start(rsm.impl.seq, v)

		finished := rsm.await_commit(rsm.impl.seq)
		// fmt.Printf("%d:\tADD %d:\t%v\n", rsm.me, rsm.impl.seq, finished)
		// fmt.Printf("")

		// mark done and apply the value
		rsm.px.Done(rsm.impl.seq)
		rsm.applyOp(finished)

		if finished == v {
			return
		}
	}
}

func (rsm *PaxosRSM) await_commit(seq int) interface{} {
	to := 10 * time.Millisecond
	for {
		stat, v := rsm.px.Status(seq)
		if stat == paxos.Decided {
			return v
		}
		time.Sleep(to)
		if to < time.Second {
			to *= 2
		}
	}
}
