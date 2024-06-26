from typing import Union, Optional, Dict, Tuple, List, Callable
import math

from knitlib import zigzagCaston, sheetBindoff
from .helpers import bnValid

from .knitout_helpers import findNextValidNeedle #?
# from .bed_needle import BedNeedle


def decEdge(obj, from_needle: int, to_needle: int, bed: Optional[str]=None): #TODO: add check for if it is a valid place to transfer to
	if from_needle < to_needle:
		obj.k.comment(f"decrease {to_needle-from_needle} on left") #debug
		#
		for i in range(to_needle-from_needle):
			if bed is None:
				if bnValid("f", from_needle+i, gauge=obj.gauge): from_bed = "f"
				elif bnValid("b", from_needle+i, gauge=obj.gauge): from_bed = "b"
				else: continue
				#
				if bnValid("b", to_needle+i, gauge=obj.gauge): to_bed = "b"
				elif bnValid("f", to_needle+i, gauge=obj.gauge): to_bed = "f"
				else:
					raise NotImplementedError("TODO: find valid needle to xfer to")
			else:
				if bnValid(bed, from_needle+i, gauge=obj.gauge): from_bed = bed
				else: continue
				#
				if bnValid(bed, to_needle+i, gauge=obj.gauge): to_bed = bed
				else:
					raise NotImplementedError("TODO: find valid needle to xfer to")
			
			obj.rackedXfer((from_bed, from_needle+i), (to_bed, to_needle+i), reset_rack=False)
	else:
		obj.k.comment(f"decrease {from_needle-to_needle} on right") #debug
		#
		for i in range(from_needle-to_needle):
			if bed is None:
				if bnValid("f", from_needle-i, gauge=obj.gauge): from_bed = "f"
				elif bnValid("b", from_needle-i, gauge=obj.gauge): from_bed = "b"
				else: continue
				#
				if bnValid("b", to_needle-i, gauge=obj.gauge): to_bed = "b"
				elif bnValid("f", to_needle-i, gauge=obj.gauge): to_bed = "f"
				else:
					raise NotImplementedError("TODO: find valid needle to xfer to")
			else:
				if bnValid(bed, from_needle-i, gauge=obj.gauge): from_bed = bed
				else: continue
				#
				if bnValid(bed, to_needle-i, gauge=obj.gauge): to_bed = bed
				else:
					raise NotImplementedError("TODO: find valid needle to xfer to")
			
			obj.rackedXfer((from_bed, from_needle-i), (to_bed, to_needle-i), reset_rack=False)
	obj.k.rack(0)


def decEdge_old(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]): #TODO: add check for if it is a valid place to transfer to
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	#
	if from_needle < to_needle:
		obj.k.comment(f"decrease {to_needle-from_needle} on left") #debug
		#
		for i in range(to_needle-from_needle):
			obj.rackedXfer((from_bed, from_needle+i), (to_bed, to_needle+i), reset_rack=False)
	else:
		obj.k.comment(f"decrease {from_needle-to_needle} on right") #debug
		#
		for i in range(from_needle-to_needle):
			obj.rackedXfer((from_bed, from_needle-i), (to_bed, to_needle-i), reset_rack=False)
	obj.k.rack(0)


def decSchoolBus(obj, from_needle: int, to_needle: int, bed: Optional[str]=None):
	if bed is None:
		if bnValid("f", from_needle, obj.gauge): bed = "f"
		elif bnValid("b", from_needle, obj.gauge): bed = "b"
		else: raise ValueError(f"from_needle: '{from_needle}' not valid on either bed")
	# from_bed, from_needle = from_bn
	# to_bed, to_needle = to_bn
	# if to_bed is None: to_bed = from_bed
	# assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
	#
	if from_needle > to_needle: #right side
		ct = from_needle-to_needle
		obj.k.comment(f"decrease {ct} on right (school bus)") #debug
		if bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		min_n = obj.getMinNeedle(bed[0])
		if from_needle-ct+1 > min_n: # valid school bus operation
			w = from_needle-min_n+1
			#
			r = max(obj.gauge, int(ct-math.fmod(ct, obj.gauge)))
			if r > obj.settings.max_rack: #TODO: #check
				ct_2 = ct*ct
				r = ct_2/(w-ct)
				r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
				assert r <= obj.settings.max_rack

			sects = ct #TODO: remove this since it is redundant
			size = math.floor(w/ct)
			# sects = ct-1
			# size = math.floor(w/(ct+1))
			start_n = from_needle

			for i in range(sects):
				# for n in range(start_n-(sects-i)*size, start_n-i*r+1):
				for n in range(start_n-(sects-1-i)*size, start_n-i*r+1):
					if bnValid(bed, n, obj.gauge): obj.rackedXfer((bed, n), (xto_bed, n-r), reset_rack=False)
				#
				# for n in range((start_n-(sects-i)*size)-r, (start_n-i*r+1)-r):
				for n in range((start_n-(sects-1-i)*size)-r, (start_n-i*r+1)-r):
						if bnValid(bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (bed, n), reset_rack=False)
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")
	else: #left side
		ct = to_needle-from_needle
		obj.k.comment(f"decrease {ct} on left (school bus)") #debug
		if bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		# if to_bed is None: to_bed = from_bed
		# assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
		#
		max_n = obj.getMaxNeedle(bed[0])
		if from_needle-ct+1 < max_n: # valid school bus operation
			w = max_n-from_needle+1
			#
			r = max(obj.gauge, int(ct-math.fmod(ct, obj.gauge))) #TODO: #check
			if r > obj.settings.max_rack: #TODO: #check
				ct_2 = ct*ct
				r = ct_2/(w-ct)
				r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
				assert r <= obj.settings.max_rack

			sects = ct #TODO: remove this since it is redundant
			size = math.floor(w/ct)
			start_n = from_needle

			for i in range(sects):
				for n in range(start_n+i*r, start_n+(sects-1-i)*size+1): #TODO: #check
					if bnValid(bed, n, obj.gauge): obj.rackedXfer((bed, n), (xto_bed, n+r), reset_rack=False)
				#
				for n in range((start_n+i*r)+r, (start_n+(sects-1-i)*size+1)+r): #TODO: #check
						if bnValid(bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (bed, n), reset_rack=False)
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")


def decSchoolBus_old(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
	#
	if from_needle > to_needle: #right side
		ct = from_needle-to_needle
		obj.k.comment(f"decrease {ct} on right (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		min_n = obj.getMinNeedle(from_bed[0])
		if from_needle-ct+1 > min_n: # valid school bus operation
			w = from_needle-min_n+1
			#
			r = max(obj.gauge, int(ct-math.fmod(ct, obj.gauge)))
			if r > obj.settings.max_rack: #TODO: #check
				ct_2 = ct*ct
				r = ct_2/(w-ct)
				r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
				assert r <= obj.settings.max_rack

			sects = ct #TODO: remove this since it is redundant
			size = math.floor(w/ct)
			# sects = ct-1
			# size = math.floor(w/(ct+1))
			start_n = from_needle

			for i in range(sects):
				# for n in range(start_n-(sects-i)*size, start_n-i*r+1):
				for n in range(start_n-(sects-1-i)*size, start_n-i*r+1):
					if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n-r), reset_rack=False)
				#
				# for n in range((start_n-(sects-i)*size)-r, (start_n-i*r+1)-r):
				for n in range((start_n-(sects-1-i)*size)-r, (start_n-i*r+1)-r):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")
	else: #left side
		ct = to_needle-from_needle
		obj.k.comment(f"decrease {ct} on left (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		# if to_bed is None: to_bed = from_bed
		# assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
		#
		max_n = obj.getMaxNeedle(from_bed[0])
		if from_needle-ct+1 < max_n: # valid school bus operation
			w = max_n-from_needle+1
			#
			r = max(obj.gauge, int(ct-math.fmod(ct, obj.gauge))) #TODO: #check
			if r > obj.settings.max_rack: #TODO: #check
				ct_2 = ct*ct
				r = ct_2/(w-ct)
				r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
				assert r <= obj.settings.max_rack

			sects = ct #TODO: remove this since it is redundant
			size = math.floor(w/ct)
			start_n = from_needle

			for i in range(sects):
				for n in range(start_n+i*r, start_n+(sects-1-i)*size+1): #TODO: #check
					if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n+r), reset_rack=False)
				#
				for n in range((start_n+i*r)+r, (start_n+(sects-1-i)*size+1)+r): #TODO: #check
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")
	

def decSchoolBus_old_old(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
	#
	if from_needle > to_needle: #right side
		ct = from_needle-to_needle
		obj.k.comment(f"decrease {ct} on right (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		min_n = obj.getMinNeedle(from_bed[0])
		if from_needle-ct+1 > min_n: # valid school bus operation
			w = from_needle-min_n+1
			#
			ct_2 = ct*ct
			r = ct_2/(w-ct)
			r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
			assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r) #TODO: #check
			start_n = from_needle

			for i in range(sects):
				for m in range(0, sects-i):
					for n in range(start_n-i*r-m*ct, (start_n-i*r-m*ct)-ct, -1):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n-r), reset_rack=False)

				for m in range(0, sects-i):
					for n in range((start_n-i*r-m*ct)-r, (start_n-i*r-m*ct)-ct-r, -1):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
				
				"""
				for n in range(start_n-i*r-(sects-i)*ct, (start_n-i*r-(sects-i)*ct)-r, -1):
					if bnValid(from_bed, n, obj.gauge):
						print(f"stack: {n}") #remove #debug
				"""
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")
	else: #left side
		ct = to_needle-from_needle
		obj.k.comment(f"decrease {ct} on left (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		# if to_bed is None: to_bed = from_bed
		# assert to_bed == from_bed, "school-bus decrease to opposite bed not supported yet"
		#
		max_n = obj.getMaxNeedle(from_bed[0])
		if from_needle-ct+1 < max_n: # valid school bus operation
			w = max_n-from_needle+1
			ct_2 = ct*ct
			r = ct_2/(w-ct)
			r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
			assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r) #TODO: #check
			start_n = from_needle

			for i in range(sects):
				for m in range(0, sects-i):
					for n in range(start_n+i*r+m*ct, (start_n+i*r+m*ct)+ct):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n+r), reset_rack=False)

				for m in range(0, sects-i):
					for n in range((start_n+i*r+m*ct)+r, (start_n+i*r+m*ct)+ct+r):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
				
				"""
				for n in range(start_n+i*r+(sects-i)*ct, (start_n+i*r+(sects-i)*ct)+r):
					if bnValid(from_bed, n, obj.gauge):
						print(f"stack: {n}") #remove #debug
				"""
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to decrease by {ct} using the school-bus method.")


def decBindoff(obj, from_needle: int, to_needle: int, bed: Optional[str]=None): #, c: Union[str, Tuple[str, List[str]]]): #TODO: have option for if double bed or not (aka use sliders instead if still want to keep needles on other bed)
	if bed is None:
		if bnValid("f", from_needle, obj.gauge): bed = "f"
		elif bnValid("b", from_needle, obj.gauge): bed = "b"
		else: raise ValueError(f"from_needle: '{from_needle}' not valid on either bed")
	# from_bed, from_needle = from_bn
	# to_bed, to_needle = to_bn
	#
	sheetBindoff(obj.k, from_needle, to_needle, obj.active_carrier, bed, obj.gauge, add_tag=False)
	# # sheetBindoff(obj.k, from_needle, to_needle, c, from_bed, obj.gauge, add_tag=False)
	# if to_bed is not None and from_bed != to_bed: obj.rackedXfer((from_bed, to_needle), to_bn)


def decBindoff_old(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]): #, c: Union[str, Tuple[str, List[str]]]): #TODO: have option for if double bed or not (aka use sliders instead if still want to keep needles on other bed)
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	#
	sheetBindoff(obj.k, from_needle, to_needle, obj.active_carrier, from_bed, obj.gauge, add_tag=False)
	# sheetBindoff(obj.k, from_needle, to_needle, c, from_bed, obj.gauge, add_tag=False)
	if to_bed is not None and from_bed != to_bed: obj.rackedXfer((from_bed, to_needle), to_bn)


#===============================================================================
def incEdge(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	#
	empty_bns = [] #TODO: use a more sophisticated method here #*
	if from_needle < to_needle:
		ct = to_needle-from_needle
		obj.k.comment(f"increase {ct} on right") #debug
		#
		for i in range(0, ct+2, 2):
			if bnValid(from_bed, from_needle-i//2, obj.gauge):
				if f"{to_bed}{to_needle-i}" in empty_bns: empty_bns.remove(f"{to_bed}{to_needle-i}") #*
				#
				obj.rackedXfer((from_bed, from_needle-i//2), (to_bed, to_needle-i), reset_rack=False)
				#
				empty_bns.append(f"{from_bed}{from_needle-i//2}") #*
	else:
		ct = from_needle-to_needle
		obj.k.comment(f"increase {ct} on left") #debug
		#
		for i in range(0, ct+2, 2):
			if bnValid(from_bed, from_needle+i//2, obj.gauge):
				if f"{to_bed}{to_needle+i}" in empty_bns: empty_bns.remove(f"{to_bed}{to_needle+i}") #*
				#
				obj.rackedXfer((from_bed, from_needle+i//2), (to_bed, to_needle+i), reset_rack=False)
				#
				empty_bns.append(f"{from_bed}{from_needle+i//2}") #*
	obj.k.rack(0)
	#*
	if obj.SPLIT_ON_EMPTY: obj.split_bns.extend(empty_bns) #*
	else: obj.twist_bns.extend(empty_bns) #*


def incSchoolBus(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	assert to_bed == from_bed, "school-bus increase to opposite bed not supported yet"
	#
	if from_needle < to_needle: #right side
		ct = to_needle-from_needle
		obj.k.comment(f"increase {ct} on right (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		min_n = obj.getMinNeedle(from_bed[0])
		if from_needle-ct+1 > min_n: # valid school bus operation
			w = from_needle-min_n+1
			#
			r = max(obj.gauge, int(ct-math.fmod(ct, obj.gauge))) #TODO: #check
			if r > obj.settings.max_rack: #TODO: #check
				ct_2 = ct*ct
				r = ct_2/(w-ct)
				r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
				assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r)
			size = math.floor(w/(sects+1))

			# start_n = from_needle - ct*sects + 1 #remove
			start_n = from_needle - size*sects + 1

			for i in range(sects):
				for m in range(i, sects):
					# for n in range(start_n+i*r+m*ct, (start_n+i*r+m*ct)+ct): #remove
					for n in range(start_n+i*r+m*size, (start_n+i*r+m*size)+size):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n+r), reset_rack=False)
				
				# assert n == from_needle+i*r #sanity check #remove #debug
				for m in range(i, sects):
					# for n in range((start_n+i*r+m*ct)+r, (start_n+i*r+m*ct)+ct+r): #remove
					for n in range((start_n+i*r+m*size)+r, (start_n+i*r+m*size)+size+r):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
				
				# for n in range(start_n+i*r+i*ct, (start_n+i*r+i*ct)+r): #remove
				for n in range(start_n+i*r+i*size, (start_n+i*r+i*size)+r):
					if bnValid(from_bed, n, obj.gauge):
						if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"{from_bed}{n}")
						else: obj.twist_bns.append(f"{from_bed}{n}") #TODO: make these splits instead #?
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to increase by {ct} using the school-bus method.")
	else: #left side
		ct = from_needle-to_needle
		obj.k.comment(f"increase {ct} on left (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		# if to_bed is None: to_bed = from_bed
		# assert to_bed == from_bed, "school-bus increase to opposite bed not supported yet"
		#
		max_n = obj.getMaxNeedle(from_bed[0])
		if from_needle+ct-1 < max_n: # valid school bus operation
			w = max_n-from_needle+1
			ct_2 = ct*ct
			r = ct_2/(w-ct)
			r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
			assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r) #TODO: #check
			start_n = from_needle + ct*sects - 1

			for i in range(sects):
				for m in range(i, sects):
					for n in range(start_n-i*r-m*ct, (start_n-i*r-m*ct)-ct, -1):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n-r), reset_rack=False)

				for m in range(i, sects):
					for n in range((start_n-i*r-m*ct)-r, (start_n-i*r-m*ct)-ct-r, -1):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
				
				for n in range(start_n-i*r-i*ct, (start_n-i*r-i*ct)-r, -1):
					if bnValid(from_bed, n, obj.gauge):
						if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"{from_bed}{n}")
						else: obj.twist_bns.append(f"{from_bed}{n}")
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to increase by {ct} using the school-bus method.")



def incSchoolBus_new(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	# assert to_bed == from_bed, "school-bus increase to opposite bed not supported yet"
	#
	if from_needle < to_needle: #right side
		if to_bed is None: to_bed = from_bed
		assert to_bed == from_bed, "school-bus increase to opposite bed not supported yet"
		#
		ct = to_needle-from_needle
		obj.k.comment(f"increase {ct} on right (school bus)") #debug
		if from_bed.startswith("f"):
			xto_bed = "bs"
		else:
			xto_bed = "fs"
		#
		min_n = obj.getMinNeedle(from_bed[0])
		if from_needle-ct+1 > min_n: # valid school bus operation
			w = from_needle-min_n+1
			ct_2 = ct*ct
			r = ct_2/(w-ct)
			r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
			assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r) #TODO: #check
			start_n = from_needle - ct*sects + 1

			for i in range(sects):
				for m in range(i, sects):
					for n in range(start_n+i*r+m*ct, (start_n+i*r+m*ct)+ct):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n+r), reset_rack=False)

				for m in range(i, sects):
					for n in range((start_n+i*r+m*ct)+r, (start_n+i*r+m*ct)+ct+r):
						if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (from_bed, n), reset_rack=False)
				
				for n in range(start_n+i*r+i*ct, (start_n+i*r+i*ct)+r):
					if bnValid(from_bed, n, obj.gauge):
						if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"{from_bed}{n}")
						else: obj.twist_bns.append(f"{from_bed}{n}") #TODO: make these splits instead #?
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to increase by {ct} using the school-bus method.")
	else: #left side
		ct = from_needle-to_needle
		obj.k.comment(f"increase {ct} on left (school bus)") #debug
		#
		other_bed is None #this will keep getting redefined if from_bed is None
		if from_bed is None:
			if to_bed is None: xtoBed = lambda n: other_bed if bnValid(other_bed, n, obj.gauge) else other_bed+"s" if bnValid(("f" if other_bed == "b" else "b"), n, obj.gauge) else None #TODO: #check
			else: xtoBed = lambda n: to_bed if bnValid(to_bed, n, obj.gauge) else None #check
		else:
			if from_bed.startswith("f"): other_bed = "b"
			else: other_bed = "f"
			#
			if to_bed is None: xtoBed = lambda n: other_bed if bnValid(other_bed, n, obj.gauge) else other_bed+"s" if bnValid(from_bed, n, obj.gauge) else None #TODO: #check
			else:
				if from_bed[0] == to_bed[0]: xtoBed = lambda n: other_bed+"s" if bnValid(to_bed, n, obj.gauge) else None #check
				else: xtoBed = lambda n: to_bed if bnValid(to_bed, n, obj.gauge) else None #check
		"""
		if from_bed.startswith("f"):
			if to_bed.startswith("f"): xto_bed = "bs"
			else: xto_bed = to_bed
		else:
			# xto_bed = "fs"
			if to_bed.startswith("b"): xto_bed = "fs"
			else: xto_bed = to_bed
		#
		if to_bed is None: to_bed = from_bed
		
		assert to_bed == from_bed, "school-bus increase to opposite bed not supported yet"
		"""
		#
		max_n = obj.getMaxNeedle(from_bed[0])
		if from_needle+ct-1 < max_n: # valid school bus operation
			w = max_n-from_needle+1
			ct_2 = ct*ct
			r = ct_2/(w-ct)
			r = max(obj.gauge, int(r-math.fmod(r, obj.gauge))) #TODO: #check
			assert r <= obj.settings.max_rack

			sects = math.ceil(ct/r) #TODO: #check
			start_n = from_needle + ct*sects - 1

			for i in range(sects):
				for m in range(i, sects):
					for n in range(start_n-i*r-m*ct, (start_n-i*r-m*ct)-ct, -1):
						if from_bed is None:
							if bnValid("f", n, obj.gauge):
								other_bed = "b"
								xto_bed = xtoBed(n-r)
								if xto_bed is not None: obj.rackedXfer(("f", n), (xto_bed, n-r), reset_rack=False)
							elif bnValid("b", n, obj.gauge):
								other_bed = "f"
								xto_bed = xtoBed(n-r)
								if xto_bed is not None: obj.rackedXfer(("b", n), (xto_bed, n-r), reset_rack=False)
						else:
							xto_bed = xtoBed(n-r)
							if xto_bed is not None: obj.rackedXfer((from_bed, n), (xto_bed, n-r), reset_rack=False)
						# if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((from_bed, n), (xto_bed, n-r), reset_rack=False)

				# if xto_bed != to_bed:
				for m in range(i, sects):
					for n in range((start_n-i*r-m*ct)-r, (start_n-i*r-m*ct)-ct-r, -1):
						if from_bed is None: #TODO: #check
							if bnValid("f", n+r, obj.gauge) and bnValid("f", n, obj.gauge) and not bnValid("b", n, obj.gauge): obj.rackedXfer(("bs", n), ("f", n), reset_rack=False)
							elif bnValid("b", n+r, obj.gauge) and bnValid("b", n, obj.gauge) and not bnValid("f", n, obj.gauge): obj.rackedXfer(("fs", n), ("b", n), reset_rack=False)
						else:
							# to_bed is None and bnValid(from_bed, n, obj.gauge) -> xfer(other_bed+"s", from_bed)
							# from_bed[0] == to_bed[0] and bnValid(to_bed, n, obj.gauge) -> xfer(other_bed+"s", to_bed)
							if to_bed is None:
								if bnValid(from_bed, n, obj.gauge): obj.rackedXfer((other_bed+"s", n), (from_bed, n), reset_rack=False)
							elif from_bed[0] == to_bed[0] and bnValid(to_bed, n, obj.gauge): obj.rackedXfer((other_bed+"s", n), (to_bed, n), reset_rack=False) # -> xfer(other_bed+"s", to_bed)
						# 
						# if bnValid(to_bed, n, obj.gauge): obj.rackedXfer((xto_bed, n), (to_bed, n), reset_rack=False)
				
				if from_bed is None:
					for n in range(start_n-i*r-i*ct, (start_n-i*r-i*ct)-r, -1):
						if bnValid("f", n, obj.gauge):
							if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"f{n}")
							else: obj.twist_bns.append(f"f{n}") #check
						elif bnValid("b", n, obj.gauge):
							if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"b{n}")
							else: obj.twist_bns.append(f"b{n}") #check
				else:
					for n in range(start_n-i*r-i*ct, (start_n-i*r-i*ct)-r, -1):
						if bnValid(from_bed, n, obj.gauge):
							if obj.SPLIT_ON_EMPTY: obj.split_bns.append(f"{from_bed}{n}")
							else: obj.twist_bns.append(f"{from_bed}{n}")
			#
			obj.k.rack(0)
		else:
			raise RuntimeError(f"not enough working needles to increase by {ct} using the school-bus method.")
	


def incCaston(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	#
	assert obj.active_carrier is not None
	if from_needle < to_needle: #right side
		# zigzagCaston(obj, BedNeedle(from_bed, from_needle+1), to_bn, obj.active_carrier)
		zigzagCaston(obj.k, from_needle+1, to_needle, obj.active_carrier, obj.gauge)
		for n in range(from_needle+1, to_needle+1):
			test_bn = ("b", n) #?
			if n in obj.avoid_bns["b"]:
				next_bn = findNextValidNeedle(obj, *test_bn, in_limits=True) #TODO: #check
				obj.rackedXfer(test_bn, next_bn)
				# obj.active_bns.append(next_bn) #TODO
	else: #left side
		zigzagCaston(obj.k, from_needle-1, to_needle, obj.active_carrier, obj.gauge)
		# zigzagCaston(obj, BedNeedle(from_bed, from_needle-1), to_bn, obj.active_carrier)


def incSplit(obj, from_bn: Tuple[str, int], to_bn: Tuple[Optional[str], int]):
	from_bed, from_needle = from_bn
	to_bed, to_needle = to_bn
	if to_bed is None: to_bed = from_bed
	#
	if from_needle < to_needle: #right side
		raise NotImplementedError("TODO")
	else: #left side
		raise NotImplementedError("TODO")
