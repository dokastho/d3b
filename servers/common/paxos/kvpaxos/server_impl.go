package kvpaxos

import (
	// "fmt"
	"sync"
)

//
// Define what goes into "value" that Paxos is used to agree upon.
// Field names must start with capital letters,
// otherwise RPC will break.
//

type Op struct {
	Seed int64
	Req  string
	Key  string
	Val  string
}

//
// additions to KVPaxos state
//
type KVPaxosImpl struct {
	set_sync sync.Mutex
	// op_sync		sync.Mutex
	db    map[string]string
	seeds map[int64]bool
}

//
// initialize kv.impl.*
//
func (kv *KVPaxos) InitImpl() {
	kv.impl.db = make(map[string]string)
	kv.impl.seeds = make(map[int64]bool)
}

//
// Handler for Get RPCs
//
func (kv *KVPaxos) Get(args *GetArgs, reply *GetReply) error {
	kv.impl.set_sync.Lock()

	// if kv.seed_status(args.Impl.Seed) {
	// 	reply.Value, _ = kv.lookup(args.Key)
	// 	reply.Err = OK
	// }

	O := Op{
		Seed: args.Impl.Seed,
		Req:  "Get",
		Key:  args.Key,
		Val:  "",
	}

	kv.rsm.AddOp(O)

	reply.Err = OK
	reply.Value, _ = kv.lookup(args.Key)

	kv.impl.set_sync.Unlock()

	return nil
}

//
// Handler for Put and Append RPCs
//
func (kv *KVPaxos) PutAppend(args *PutAppendArgs, reply *PutAppendReply) error {
	kv.impl.set_sync.Lock()

	if kv.seed_status(args.Impl.Seed) {
		reply.Err = OK
		kv.impl.set_sync.Unlock()
		return nil
	}

	O := Op{
		Seed: args.Impl.Seed,
		Req:  args.Op,
		Key:  args.Key,
		Val:  args.Value,
	}

	kv.rsm.AddOp(O)

	reply.Err = OK
	kv.impl.set_sync.Unlock()

	return nil
}

//
// Execute operation encoded in decided value v and update local state
//
// Don't forget to call the Paxos Done() method when a KVPaxos server
// has processed an instance and will no longer need it or any previous
// instance.
//
func (kv *KVPaxos) ApplyOp(v interface{}) {

	op := v.(Op)

	// if kv.seed_status(op.Seed) {
		// fmt.Printf("Duplicate apply sent for %v\n", v)
		// return
	// }

	// fmt.Printf("%d:\tAPPLY:\t%v\n", kv.me, v)
	// fmt.Printf("")

	if op.Req == "Get" {
		// no-op
	} else if op.Req == "Put" {
		kv.do_put_append(op.Key, op.Val, op.Req)
	} else if op.Req == "Append" {
		kv.do_put_append(op.Key, op.Val, op.Req)
	}

	kv.complete_seed(op.Seed)
}

func (kv *KVPaxos) lookup(key string) (string, bool) {
	kv.mu.Lock()
	val, ok := kv.impl.db[key]
	kv.mu.Unlock()
	return val, ok
}

func (kv *KVPaxos) seed_status(seed int64) bool {
	kv.mu.Lock()
	_, ok := kv.impl.seeds[seed]

	// implicitly add this seed to the map
	if !ok {
		kv.impl.seeds[seed] = false
	}

	b := kv.impl.seeds[seed]

	kv.mu.Unlock()
	return b
}

func (kv *KVPaxos) complete_seed(seed int64) {
	kv.mu.Lock()
	kv.impl.seeds[seed] = true
	kv.mu.Unlock()
}

func (kv *KVPaxos) do_put_append(key string, val string, req string) {
	kv.mu.Lock()

	original, ok := kv.impl.db[key]
	if !ok {
		original = ""
	}

	if req == "Append" {
		// fmt.Printf("Append %v to %v for key %v", val, original, key)
		val = original + val
	// } else if req == "Put" {
		// fmt.Printf("Put %v, original %v for key %v", val, original, key)
	}

	kv.impl.db[key] = val

	kv.mu.Unlock()
}
