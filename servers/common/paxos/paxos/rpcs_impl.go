package paxos

import "fmt"

// In all data types that represent RPC arguments/reply, field names
// must start with capital letters, otherwise RPC will break.

const (
	OK          = "OK"
	Reject      = "Reject"
)

type Response string

type PrepareArgs struct {
	Seq			int
	N			int
	V			interface{}

	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int

	Identity	string

	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int
}

type PrepareReply struct {
	Res			Response
	Seq			int
	N_a			int
	V_a			interface{}
	
	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int
	
	Identity	string
	
	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int

	Valid		bool
}

type AcceptArgs struct {
	Seq			int
	N			int
	V			interface{}

	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int

	Identity	string

	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int
}

type AcceptReply struct {
	Res			Response
	Seq			int
	N			int

	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int

	Identity	string

	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int
}

type DecidedArgs struct {
	Seq			int
	N			int
	V			interface{}
	
	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int	
	
	Identity	string

	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int
}

type DecidedReply struct {
	Res			Response
	Seq			int
	// V			interface{}
	
	// piggybacked max_seq that each instance is aware of (for Max())
	Max_seq		int
	
	Identity	string
	
	// piggybacked max_done seq (so that instances can update Min()) 
	Max_done	int
}

func (px *Paxos) Prepare(args *PrepareArgs, reply *PrepareReply) error {
	me := px.whoami()
	px.impl.set_sync.Lock()
	defer px.impl.set_sync.Unlock()

	px.update_peer_max(args.Identity, args.Max_done)
	px.update_max_seq(args.Seq)

	// default to reject
	reply.Res = Reject
	reply.Max_done = px.get_max_done()
	reply.Max_seq = px.get_max_seq()
	reply.N_a = -1
	reply.Identity = me
	reply.Valid = true
	reply.Seq = args.Seq

	px.mu.Lock()
	datum := px.rpc_inst_init(args.Seq, true)

	if args.N > datum.N_p {
		if args.N > px.impl.max_n {
			px.impl.max_n = args.N
		}
		// reply with accept
		reply.Res = OK
		datum.N_p = args.N
		
		reply.N_a = datum.N_a
		reply.V_a = datum.V_a
	}
	
	px.impl.log[args.Seq] = datum
	px.print_log()
	px.mu.Unlock()
	return nil
}

func (px *Paxos) Accept(args *AcceptArgs, reply *AcceptReply) error {
	px.impl.set_sync.Lock()
	defer px.impl.set_sync.Unlock()


	px.update_peer_max(args.Identity, args.Max_done)
	px.update_max_seq(args.Seq)

	reply.Res = Reject
	reply.Max_done = px.get_max_done()
	reply.Max_seq = px.get_max_seq()
	reply.Identity = px.whoami()

	me := px.whoami()

	px.mu.Lock()
	datum := px.rpc_inst_init(args.Seq, false)

	if args.N >= datum.N_p {
		// update state
		datum.N_a = args.N
		if VERBOSE {
			fmt.Printf("Accept: %s set N_a to %d for seq %d, val %v\n", me, args.N, args.Seq, args.V)
		}
		
		datum.N_p = args.N
		datum.V_a = args.V

		// set values in reply
		reply.N = args.N
		reply.Res = OK
	}
	px.impl.log[args.Seq] = datum
	px.print_log()
	px.mu.Unlock()
	return nil
}

func (px *Paxos) Learn(args *DecidedArgs, reply *DecidedReply) error {
	px.impl.set_sync.Lock()
	defer px.impl.set_sync.Unlock()

	px.update_peer_max(args.Identity, args.Max_done)
	px.update_max_seq(args.Seq)

	me := px.whoami()

	px.mu.Lock()
	datum := px.rpc_inst_init(args.Seq, false)
	
	// update log
	datum.Status = Decided
	datum.V_a = args.V
	datum.N_a = args.N
	if VERBOSE {
		fmt.Printf("Learn: %s set N_a to %d for seq %d, val %v\n", me, args.N, args.Seq, args.V)
	}

	datum.N_p = args.N

	reply.Res = OK
	reply.Max_done = px.impl.max_done
	reply.Max_seq = px.impl.max_seq

	px.impl.log[args.Seq] = datum
	px.print_log()
	px.mu.Unlock()
	return nil
}

//
// add RPC handlers for any RPCs you introduce.
//

func (px * Paxos) rpc_inst_init(seq int, p_phase bool) Instance_t {
	datum := Instance_t{
		Status: Pending,
		N_p: -1,
		N_a: -1,
		V_a: nil,
	}

	inst, exists := px.impl.log[seq]
	if exists {
		datum = inst
	}
	return datum
}