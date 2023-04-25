package paxos

import (
	"fmt"
	"sort"
	"sync"
	"time"

	"d3b/common"
)

//
// additions to Paxos state.
//
type PaxosImpl struct {
	log          map[int]Instance_t
	peer_maxdone map[string]int

	max_seq  int
	max_done int
	max_n    int

	paxos_min int

	set_sync sync.Mutex
}

type Instance_t struct {
	Status Fate
	N_a    int
	N_p    int
	V_a    interface{}
}

const (
	Prepare = "Prepare"
	Accept  = "Accept"
	Learn   = "Learn"
)

// const VERBOSE = true
const VERBOSE = false

//
// basic idea, each instance is for one
//

//
// your px.impl.* initializations here.
//
func (px *Paxos) initImpl() {
	// px.impl.set_sync.Lock()
	px.mu.Lock()

	px.impl.max_done = -1

	px.impl.log = make(map[int]Instance_t)
	px.impl.peer_maxdone = make(map[string]int)
	for i, v := range px.peers {
		if i == px.me {
			continue
		}
		px.impl.peer_maxdone[v] = px.impl.max_done
	}
	px.impl.max_seq = -1
	px.impl.max_n = 0
	px.impl.paxos_min = -1

	px.mu.Unlock()
	// px.impl.set_sync.Unlock()
}

//
// the application wants paxos to start agreement on
// instance seq, with proposed value v.
// Start() returns right away; the application will
// call Status() to find out if/when agreement
// is reached.
//
func (px *Paxos) Start(seq int, v interface{}) {
	// concurrency later...
	if VERBOSE {
		fmt.Printf("Start: %d, ", seq)
		fmt.Println(v)
	}
	go px.do_paxos(seq, v)

	// px.do_paxos(seq, v)
}

//
// the application on this machine is done with
// all instances <= seq.
//
// see the comments for Min() for more explanation.
//
func (px *Paxos) Done(seq int) {
	if seq > px.get_max_done() {
		px.set_max_done(seq)
	}

	// do garbage collection
	px.update_min()
}

//
// the application wants to know the
// highest instance sequence known to
// this peer.
//
func (px *Paxos) Max() int {
	return px.get_max_seq()
}

//
// Min() should return one more than the minimum among z_i,
// where z_i is the highest number ever passed
// to Done() on peer i. A peer's z_i is -1 if it has
// never called Done().
//
// Paxos is required to have forgotten all information
// about any instances it knows that are < Min().
// The point is to free up memory in long-running
// Paxos-based servers.
//
// Paxos peers need to exchange their highest Done()
// arguments in order to implement Min(). These
// exchanges can be piggybacked on ordinary Paxos
// agreement protocol messages, so it is OK if one
// peer's Min does not reflect another peer's Done()
// until after the next instance is agreed to.
//
// The fact that Min() is defined as a minimum over
// *all* Paxos peers means that Min() cannot increase until
// all peers have been heard from. So if a peer is dead
// or unreachable, other peers' Min()s will not increase
// even if all reachable peers call Done(). The reason for
// this is that when the unreachable peer comes back to
// life, it will need to catch up on instances that it
// missed -- the other peers therefore cannot forget these
// instances.
//
func (px *Paxos) Min() int {
	px.update_min()
	return px.get_paxos_min() + 1
}

//
// the application wants to know whether this
// peer thinks an instance has been decided,
// and if so, what the agreed value is. Status()
// should just inspect the local peer state;
// it should not contact other Paxos peers.
//
func (px *Paxos) Status(seq int) (Fate, interface{}) {

	if seq < px.get_paxos_min() {
		return Forgotten, nil
	} else if seq > px.get_max_seq() {
		return Pending, nil
	} else {
		val, ok := px.read_slot(seq)
		if ok {
			return val.Status, val.V_a
		} else {
			// // fmt.Printf("Error: px.Status cannot return a value\n")
			return Forgotten, nil
		}
	}
}

func (px *Paxos) do_paxos(seq int, v interface{}) {

	// px.impl.paxos_sync.Lock()
	// defer px.impl.paxos_sync.Unlock()

	var majority_accept bool
	var zero_replies bool
	var retry bool
	var statuses []string

	px.update_max_seq(seq)

	// me := px.whoami()

	n := px.get_max_n()
	for {
		if retry {
			if px.isdead() {
				break
			}
			time.Sleep(10 * time.Millisecond)
			retry = false
		}
		n += 1
		ob, exists := px.read_slot(seq)
		if exists && ob == v {
			fmt.Printf("duplicate detected %v\n", v)
		}

		p_replies := px.prepare_phase(seq, n, v)

		statuses = nil
		// get status from each reply
		for _, vx := range p_replies {
			statuses = append(statuses, string(vx.Res))
			px.update_peer_max(vx.Identity, vx.Max_done)
			px.update_max_seq(vx.Max_seq)
		}

		// garbage collection step
		px.update_min()

		majority_accept = px.did_majority_accept(statuses)
		zero_replies = len(p_replies) == 0

		// majority did not accept
		// forget?
		if !majority_accept && !zero_replies {
			// fmt.Printf("%s: prepare phase abort with n = %d, key = %d\n", me, n, seq)
			// remove from slot
			// px.delete_log(n)
			retry = true
			continue
		}

		do_accept := px.do_accept_phase(n, p_replies)

		if do_accept {
			// start accept phase
			var a_replies []AcceptReply
			a_replies, v = px.accept_phase(seq, n, v, p_replies)

			statuses = nil
			// get status from each reply
			for _, vx := range a_replies {
				statuses = append(statuses, string(vx.Res))
				px.update_peer_max(vx.Identity, vx.Max_done)
				px.update_max_seq(vx.Max_seq)
			}

			// garbage collection step
			px.update_min()

			majority_accept = px.did_majority_accept(statuses)
			zero_replies = len(p_replies) == 0

			// majority did not accept
			// forget?
			if !majority_accept && !zero_replies {
				// fmt.Printf("%s: accept phase abort with n = %d, key = %d\n", me, n, seq)
				// remove from slot
				// px.delete_log(n)
				retry = true
				continue
			}
		}

		px.learn_phase(seq, n, v)

		// garbage collection step
		// px.Done(seq)
		px.update_min()

		break
	}

}

func (px *Paxos) prepare_phase(seq int, n int, v interface{}) []PrepareReply {

	// get peers from state
	peers := px.get_peers()
	n_peers := len(peers)

	goal := n_peers/2 + 1
	affirms := 0

	// request content & replies slice
	var replies []PrepareReply

	for p := 0; p < n_peers; p++ {

		if (goal - affirms) > (n_peers - p) {
			break
		}

		args := PrepareArgs{seq, n, v, px.get_max_seq(), px.whoami(), px.get_max_done()}
		reply := PrepareReply{}

		if p == px.me {
			px.Prepare(&args, &reply)
		} else {
			common.Call(peers[p], "Paxos.Prepare", &args, &reply)
		}

		// efficiency
		if reply.Res == OK {
			affirms += 1
		}

		// save reply
		replies = append(replies, reply)
		if affirms == goal {
			break
		}
	}

	return replies
}

// question: should I discard replies that are not affirmative?
func (px *Paxos) accept_phase(seq int, n int, v interface{}, p_replies []PrepareReply) ([]AcceptReply, interface{}) {
	max_n_a := 0 // TODO: check!
	v_prime := v

	me := px.whoami()

	if VERBOSE {
		fmt.Printf("\t%s: After proposing %v with N = %d I got these replies:\n", me, v, n)
	}

	// find max n_a, set v_prime if one found
	for i := range p_replies {
		reply := p_replies[i]

		if !reply.Valid {
			continue
		}
		if VERBOSE {
			fmt.Printf("\t\tV_a = %v, N_a = %d\n", reply.V_a, reply.N_a)
		}
		if reply.N_a >= max_n_a {
			max_n_a = reply.N_a
			v_prime = reply.V_a
		}
	}
	if VERBOSE {
		fmt.Printf("\t%s: I proposed %v with N = %d and decided on %v, max N_a = %d", me, v, n, v_prime, max_n_a)

		fmt.Println()
	}

	// get peers from state
	peers := px.get_peers()
	n_peers := len(peers)

	goal := n_peers/2 + 1
	affirms := 0

	// request content & replies slice
	var replies []AcceptReply

	for p := 0; p < n_peers; p++ {

		if (goal - affirms) > (n_peers - p) {
			break
		}
		args := AcceptArgs{seq, n, v_prime, px.get_max_seq(), px.whoami(), px.get_max_done()}
		reply := AcceptReply{}

		if p == px.me {
			px.Accept(&args, &reply)
		} else {
			common.Call(peers[p], "Paxos.Accept", &args, &reply)
		}

		// efficiency
		if reply.Res == OK {
			affirms += 1
		}

		// save reply
		replies = append(replies, reply)
		if affirms == goal {
			break
		}
	}

	return replies, v_prime
}

func (px *Paxos) learn_phase(seq int, n int, v interface{}) []DecidedReply {

	// get peers from state
	peers := px.get_peers()
	n_peers := len(peers)

	// request content & replies slice
	var replies []DecidedReply

	for p := 0; p < n_peers; p++ {

		args := DecidedArgs{
			seq,
			n,
			v,
			px.get_max_seq(),
			px.whoami(),
			px.get_max_done(),
		}
		reply := DecidedReply{}

		if p == px.me {
			px.Learn(&args, &reply)
		} else {
			common.Call(peers[p], "Paxos.Learn", &args, &reply)
		}

		// save reply
		replies = append(replies, reply)
	}

	return replies
}

func (px *Paxos) update_min() {
	px.mu.Lock()
	min := px.impl.max_done

	// want minimum in the network
	for _, v := range px.impl.peer_maxdone {
		if v < min {
			min = v
		}
	}

	px.impl.paxos_min = min

	for seq := range px.impl.log {
		if seq <= min {
			delete(px.impl.log, seq)
		}
	}
	px.mu.Unlock()
}

func (px *Paxos) update_peer_max(peer string, max_done int) {
	px.mu.Lock()
	if px.impl.peer_maxdone[peer] < max_done {
		px.impl.peer_maxdone[peer] = max_done
	}
	px.mu.Unlock()
	px.update_min()
}

func (px *Paxos) get_max_n() int {
	px.mu.Lock()
	m := px.impl.max_n
	px.mu.Unlock()
	return m
}

func (px *Paxos) get_peers() []string {
	px.mu.Lock()
	peers := px.peers
	px.mu.Unlock()
	return peers
}

func (px *Paxos) get_paxos_min() int {
	px.mu.Lock()
	val := px.impl.paxos_min
	px.mu.Unlock()
	return val
}

func (px *Paxos) get_max_seq() int {
	px.mu.Lock()
	val := px.impl.max_seq
	px.mu.Unlock()
	return val
}

func (px *Paxos) set_max_seq(val int) {
	px.mu.Lock()
	px.impl.max_seq = val
	px.print_log()
	px.mu.Unlock()
}

func (px *Paxos) get_max_done() int {
	px.mu.Lock()
	val := px.impl.max_done
	px.mu.Unlock()
	return val
}

func (px *Paxos) set_max_done(val int) {
	px.mu.Lock()
	px.impl.max_done = val
	for seq, v := range px.impl.log {
		if seq <= val {
			// v.Status = Forgotten
			px.impl.log[seq] = v
		}
	}
	px.print_log()
	px.mu.Unlock()
}

func (px *Paxos) did_majority_accept(replies []string) bool {
	// check if majority of peers accepted
	peers := px.get_peers()
	goal := len(peers)/2 + 1
	affirms := 0

	for i := range replies {
		rep := replies[i]
		if rep == OK {
			affirms += 1
		}
	}
	return affirms >= goal
}

func (px *Paxos) read_slot(key int) (Instance_t, bool) {
	px.mu.Lock()
	val, ok := px.impl.log[key]
	px.mu.Unlock()
	return val, ok
}

func (px *Paxos) whoami() string {
	px.mu.Lock()
	me := px.peers[px.me]
	px.mu.Unlock()
	return me
}

func (px *Paxos) print_log() {
	if !VERBOSE {
		// if true {
		return
	}
	me := px.peers[px.me]
	fmt.Printf("\tMachine: %s\n\n", me)

	fmt.Printf("\t\tLocal Maximum Sequence: %d\n\t\tMinimum Decided Sequence: %d\n", px.impl.max_seq, px.impl.max_done)

	fmt.Printf("\tPeers:\n")
	for _, peer := range px.peers {
		fmt.Printf("\t\t%s\n", peer)
	}

	fmt.Printf("\tLog\n")
	L := px.impl.log
	var sorted_keys []int
	for key := range L {
		sorted_keys = append(sorted_keys, key)
	}

	sort.Ints(sorted_keys)

	for i := range sorted_keys {
		seq := sorted_keys[i]
		v := L[seq]

		fates := [3]string{"Decided", "Pending", "Forgotten"}
		fmt.Printf("\t\t%d (%d): ", seq, v.N_a)
		fmt.Printf("%v, ", v.V_a)
		fmt.Printf("%s\n", fates[v.Status-1])
		fmt.Printf("\t\t\tN_a: %d\n\t\t\tN_p: %d\n", v.N_a, v.N_p)
	}
	fmt.Printf("\n")
}

func (px *Paxos) update_max_seq(seq int) {
	if seq > px.get_max_seq() {
		px.set_max_seq(seq)
	}
}

// figure out memory freeing
// verify efficiency
// ask about concurrency
func (px *Paxos) do_accept_phase(n_p int, replies []PrepareReply) bool {
	var n_as []int

	for _, reply := range replies {
		if reply.Res == OK {
			n_as = append(n_as, reply.N_a)
		}
	}

	max := n_as[0]
	for _, n := range n_as {
		if n != max {
			return true // should do accept
		}
		if n > max {
			max = n
		}
	}
	// also if va == na
	return max < n_p
}
