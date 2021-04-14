import json
import codecs
import types
import sys
import math
import random

def sieve(n):
    """
    Taken from
    https://stackoverflow.com/questions/16004407/
    a-fast-prime-number-sieve-in-python
    """
    sz = n//2
    s = [1]*sz
    limit = int(n**0.5)
    for i in range(1,limit):
        if s[i]:
            val = 2*i+1
            tmp = ((sz-1) - i)//val 
            s[i+val::val] = [0]*tmp
    return [2] + [i*2+1 for i, v in enumerate(s) if v and i>0]

primes=sieve(10000)

def modpow(a,e,n):
    """Returns a^e (mod n).
    More efficient for large values than directly computing."""
    if(n<1):
        return -1
    b=bin(e)[2:]
    prod=1
    current=a
    for i in range(len(b)):
        if(b[-i-1]=='1'):
            prod *= current
            prod %= n
        current *= current
        current %= n
    return prod

initialCertainty=1 #Value to get approximation for Bayesian probability a
#number given by Miller-Rabin is prime
for p in primes:
        initialCertainty*=1+1/p
def v(n,d):
    """Maximum e such that d^e divides n."""
    if n<1 or d<2:
        return -1
    count=0
    while n%d==0:
        n//=d
        count+=1
    return count
def millerRabin(n,prob=-1,checked=-1):
    global initialCertainty
    """Probabilistic primality test. Defaults to 99.999% Bayesian expectation
    with priors given by PNT but can be set higher with prob.
    You may include an optional array of primes which are known
    not to divide the integer (defaults to the primes <10000
    for the sake of the standard prime)."""
    if prob==-1:
        prob=0.99999
    if checked != -1:
        initialCertainty=1
        for p in checked:
            initialCertainty*=1+1/p
    desired=1/(1-prob)
    certainty=1/math.log(n)
    certainty/=1-certainty
    certainty*=initialCertainty
    
    s=v(n-1,2)
    d=(n-1)//2**s
    count=0
    while certainty<desired or count<10:
        a=random.randint(1,n-1)
        k=modpow(a,d,n)
        if k != 1:
            r=0
            while k%n!=n-1 and r<s:
                k=(k**2)%n
                r+=1
            if r==s:
                return False
        certainty*=4
        count+=1
    return True
def prime(n,prob=-1):
    """Deterministic up to 100,000,000,
    uses Miller-Rabin afterwards to Bayesian probability of at least prob.
    Default value set to 99.999%.
    """
    if(n<2):
        return False
    if(n==2):
        return True
    for p in primes:
        if (n%p==0):
            return False
        elif (p*p>n):
            return True
    return millerRabin(n,prob)
#end book imports

#experimental rich printing from 
#https://www.willmcgugan.com/blog/tech/post/real-working-hyperlinks-in-the-terminal-with-rich/
#and
#https://github.com/willmcgugan/rich
#didn't work in my terminal, so avoided for now

#import rich
#from rich import print as rich_print

names=['']+codecs.open("names.txt",encoding='utf-8').read().split('\n')[4:]

A=open("stripped.txt").read().split('\n')
def qint(l):
    nl=[]
    for i in range(1,len(l)):
        if l[i]=='':
            return nl
        else:
            nl+=[int(l[i])]
    return nl
A=[[]]+[qint(e.split(',')) for e in A[4:]]

def paren_split(s):
    bits=[]
    depth = 0
    current=''
    for c in s:
        if c in '([{':
            if depth==0:
                if len(current.strip())>0: #don't count spacing between parens
                    bits.append([current,0])
                current=''
            else:
                current+=c
            depth+=1
        elif c in '}])':
            depth-=1
            if depth<=0:
                if len(current.strip())>0: #don't count spacing between parens
                    bits.append([current,1])
                current=''
            else:
                current+=c
        else:
            current+=c
    if len(current.strip())>0: #don't count spacing between parens
        bits.append([current,int(depth>0)])
    return bits

def tparse(s,x,l,p):
    #parse a final search term (no * or ?), given a previous term in the sequence
    #x = current a-term
    #l = list of functions
    #p = previous term
    if isinstance(s, types.FunctionType):
        return s(x)
    try:
        v=int(s)
        return x==v
    except ValueError:
        s = s.strip() #remove any extraneous spaces
        if s=='_' or s=='': #empty string means that "*" parses as "_*"
            #this comes first, so all further clauses 
            #can assume s has at least one character
            return True
        elif '(' in s or '[' in s: #evaluate parentheticals
            paren_clauses = paren_split(s)
            new_s = ''
            for clause, is_paren in paren_clauses:
                if is_paren: #evaluate the stuff in the parenthetical first
                    new_s+=str(tparse(clause,x,l,p)) #either 'True' or 'False'
                else: #don't change this
                    new_s+=clause
            return tparse(new_s,x,l,p)
        
        elif '|' in s: #logical OR of several options
            #lowest precedence, so outermost split
            qs=s.split('|')
            for q in qs:
                #ignore q='' so that || doesn't mess things up
                if q!='' and tparse(q,x,l,p):
                    return True
            return False
        elif '&' in s: #AND takes precedence over OR
            qs=s.split('&')
            for q in qs:
                #ok if q='' because we'll just AND it with true
                if not tparse(q,x,l,p):
                    return False
            return True
        elif s[0]=='!': #negation has the highest precedence, so comes last
            return not tparse(s[1:],x,l,p)
        elif s.lower() == 'true':
            return True
        elif s.lower() == 'false':
            return False
        elif s.lower() == 'even':
            return (x%2==0)
        elif s.lower() == 'odd':
            return x%2==1
        elif s.lower() == 'prime':
            return prime(x) #note this is a probabilistic test for large primes
        elif '-' in s[1:]: #range, e.g. "1 - 3"
            #if the lower end is a negative number, s[0] might be '-'
            #so we restrict to the 
            i=s[1:].index('-')+1 
            a=int(s[:i]) #first number
            b=int(s[i+1:]) #second number
            return min(a,b)<=x<=max(a,b)
        elif '%' in s: #e.g. "3%4" means 3 mod 4 ("%4" defaults to 0 mod 4)
            i=s.index('%')
            try:
                a=int(s[:i])
            except ValueError:
                a==0
            b=int(s[i+1:])
            return x%b == a%b
        elif s == '<' or s=='-':
            return x<p
        elif s == '<=':
            return x<=p
        elif s == '>' or s=='+':
            return x>p
        elif s == '>=':
            return x>=p
        elif s == '=':
            return x==p
        elif s[0] == '=': #e.g. "=2"
            return x==int(s[1:])
        elif s[0] in ['<','>']:
            if s[0]=='<':
                if s[1]=='=':
                    return (x<=int(s[2:]))
                else:
                    return (x<int(s[1:]))
            else:
                if s[1]=='=':
                    return (x>=int(s[2:]))
                else:
                    return (x>int(s[1:]))
        elif s[0] == 'f': #referring to a function
            try:
                i=int(s[1:])
                return l[i-1](x)
            except ValueError:
                print("Unrecognized f-index:",s)
        else:
            print("Unrecognized final term:",s)
            print(0/0)
    
def parse(s,a,l=[],p=0,verbose=False,t=0): #Does sequence a satisfy search s?
    if verbose:
        print('  '*t+str(s),a,p)
    if (a==[] and s==[]) or (a==[] and len(s)==1 and s[0][-1]=='*'): #run out of terms and queries
                                                                     #or final query is a wildcard
        if verbose:
            print('  '*t+"returning 2")
        return 2 #our "really a match" return value
    elif s==[]: #more terms, but no more queries
        if verbose:
            print('  '*t+"returning 0")
        return 0
    elif a==[]: #if the sequence were extended, it could match
        if verbose:
            print('  '*t+"returning 1")
        return 1 #only case when this is returned
    c = s[0] #current search term
    ax = a[0] #current focus term
    if type(c)==str and c[-1]=='*':
        absent = parse(s[1:],a,l,p,verbose,t+1) #no more * terms
        if absent==2: #save time
            return absent
        works = tparse(c[:-1],ax,l,p) #does the next term satisfy the asterisk condition?
        if works: #we can run the same s-terms with the next bit of the list
            present = parse(s,a[1:],l,ax,verbose,t+1)
        else:
            present=0
        return max(present, absent) #best return type of the two of these
    elif type(c)==str and c[-1]=='?': #this term may not exist
        absent = parse(s[1:],a,l,p,verbose,t+1) #if there's no such term, previous is same (and a doesn't shrink)
        if absent==2: #save time
            return absent
        works = tparse(c[:-1],ax,l,p) #does the next term satisfy the question mark condition?
        if works:
            present = parse(s[1:],a[1:],l,ax,verbose,t+1) #note that we now have the previous term as the current term
        else:
            present = False #if we can't take a question mark term, then this fails
        
        return max(present, absent) #either way works, take the best one
    else:
        works = tparse(c,ax,l,p) #does the current term satisfy the search?
        if works:
            return parse(s[1:],a[1:],l,ax,verbose,t+1)
        else:
            if verbose:
                print('  '*t+"returning 0")
            return 0
    pass


def search(s,l=[],show=5):
    if type(s)==str: #might be a list of strings and functions
        if s=='':
            print("Empty search!")
            return 0
        s=s.split(',')
        s=[e.strip() for e in s]
        if s[-1]=='':
            s[-1]='_' #just so the next check doesn't fail
        if s[-1][-1]=='*':
            pass
        elif s[-1][-1]=='!':#end of sequence
            s=s[:-1]
        else:
            if s[-1]=='+':
                s[-1] = '>=*'
            elif s[-1]=='++':
                s[-1] = '>*'
            else:
                s.append('*')
    valid_indices=[]
    for i in range(1,len(A)): #start at A000001
        a=A[i]
        v = parse(s,a,l)
        if v==2:
            valid_indices.append(i)
            if len(valid_indices)<=show:
                print(names[i])
                print(a)
    if len(valid_indices)>show:
        extras = len(valid_indices)-show
        print("%d more result%s not shown." % (extras,['s',''][extras == 1]))
    elif valid_indices==[]:
        print("No compatible results found.")
    else:
        print('='*20)
    return valid_indices

ipt=''
while len(ipt)==0 or ipt[0]!='q':
    ipt=input()
    r=search(ipt,show=10)
