package kvpaxos

import (
	"sync"

	"d3b/common"
)

//
// any additions to Clerk state
//
// notes
// Your KVPaxos client code should try different replicas it
// knows about until one responds. A KVPaxos replica that is
// part of a majority of replicas that can all reach each
// other should be able to serve client requests.
//
type ClerkImpl struct {
	set_sync		sync.Mutex
}

//
// initialize ck.impl state
//
func (ck *Clerk) InitImpl() {
}

//
// fetch the current value for a key.
// returns "" if the key does not exist.
// keeps trying forever in the face of all other errors.
//
func (ck *Clerk) Get(key string) string {
	ck.impl.set_sync.Lock()
	defer ck.impl.set_sync.Unlock()

	seed := common.Nrand()

	val := ""

	ok := false
	for !ok {
		// try different replicas
		for _, srv := range ck.servers {
			args_impl := GetArgsImpl{seed}
			args := GetArgs{key, args_impl}
			reply := &GetReply{}

			ok = common.Call(srv, "KVPaxos.Get", args, reply)
			if reply.Err != OK {
				ok = false
			}
			if ok {
				val = reply.Value
				break
			}
		}
	}
	return val
}

//
// shared by Put and Append; op is either "Put" or "Append"
//
func (ck *Clerk) PutAppend(key string, value string, op string) {
	ck.impl.set_sync.Lock()
	defer ck.impl.set_sync.Unlock()
	
	seed := common.Nrand()

	ok := false
	for !ok {
		// try different replicas
		for _, srv := range ck.servers {
			args_impl := PutAppendArgsImpl{seed}
			args := PutAppendArgs{key, value, op, args_impl}
			reply := &PutAppendReply{}

			ok = common.Call(srv, "KVPaxos.PutAppend", args, reply)
			if reply.Err != OK {
				ok = false
			}
			if ok {
				break
			}
		}
	}
}