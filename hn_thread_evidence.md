# HN thread evidence – Python 3.12 (id 37737519)

Tool: `python3 ./hackernews get-item --id <id>` via the bundled Hacker News CLI (`hackernews get-item --id <id>`)
Evidence captured before README sentiment summary was prepared.

## 37737519 – qsort

Python 3.12

## 37737692 – bloopernova

What&#x27;s new: <a href="https:&#x2F;&#x2F;docs.python.org&#x2F;dev&#x2F;whatsnew&#x2F;3.12.html" rel="nofollow noreferrer">https:&#x2F;&#x2F;docs.python.org&#x2F;dev&#x2F;whatsnew&#x2F;3.12.html</a><p>Summary, sorry for poor formatting, I&#x27;m not sure HN can do a list of any kind?<p><i>New features</i><p>More flexible f-string parsing, allowing many things previously disallowed (PEP 701).<p>Support for the buffer protocol in Python code (PEP 688).<p>A new debugging&#x2F;profiling API (PEP 669).<p>Support for isolated subinterpreters with separate Global Interpreter Locks (PEP 684).<p>Even more improved error messages. More exceptions potentially caused by typos now make suggestions to the user.<p>Support for the Linux perf profiler to report Python function names in traces.<p>Many large and small performance improvements (like PEP 709 and support for the BOLT binary optimizer), delivering an estimated 5% overall performance improvement.<p><i>Type annotations</i><p>New type annotation syntax for generic classes (PEP 695).<p>New override decorator for methods (PEP 698).<p><i>Deprecations</i><p>The deprecated wstr and wstr_length members of the C implementation of unicode objects were removed, per PEP 623.<p>In the unittest module, a number of long deprecated methods and classes were removed. (They had been deprecated since Python 3.1 or 3.2).<p>The deprecated smtpd and distutils modules have been removed (see PEP 594 and PEP 632. The setuptools package continues to provide the distutils module.<p>A number of other old, broken and deprecated functions, classes and methods have been removed.<p>Invalid backslash escape sequences in strings now warn with SyntaxWarning instead of DeprecationWarning, making them more visible. (They will become syntax errors in the future.)<p>The internal representation of integers has changed in preparation for performance enhancements. (This should not affect most users as it is an internal detail, but it may cause problems for Cython-generated code.)

## 37737736 – bluish29

I think the support for isolated sub-interpreters with separate Global Interpreter Locks is the most interesting new feature in python. It is doubtful not the best way to offer some sort of concurrency but still a step closer to maybe one day get rid of GILs.

## 37737933 – formerly_proven

Breaking changes:<p>PEP 632: Remove the distutils package. See the migration guide for advice replacing the APIs it provided. The third-party Setuptools package continues to provide distutils, if you still require it in Python 3.12 and beyond.<p>gh-95299: Do not pre-install setuptools in virtual environments created with venv. This means that distutils, setuptools, pkg_resources, and easy_install will no longer available by default; to access these run pip install setuptools in the activated virtual environment.<p>The asynchat, asyncore, and imp modules have been removed, along with several unittest.TestCase method aliases.

## 37738392 – dandiep

Ooh, seems there is a new syntax for declaring the types of kwargs [1]:<p><pre><code>  from typing import TypedDict, Unpack
  
  class Movie(TypedDict):
    name: str
    year: int

  def foo(*kwargs: Unpack[Movie]): ...
</code></pre>
Maybe now I&#x27;ll be able to actually figure out what data to send libraries without actually reading their source code.<p>1. <a href="https:&#x2F;&#x2F;docs.python.org&#x2F;3.12&#x2F;whatsnew&#x2F;3.12.html#pep-692-using-typeddict-for-more-precise-kwargs-typing" rel="nofollow noreferrer">https:&#x2F;&#x2F;docs.python.org&#x2F;3.12&#x2F;whatsnew&#x2F;3.12.html#pep-692-usin...</a>

## 37739502 – georgehotelling

I&#x27;m just happy for itertools.batched for chunking iterables: <a href="https:&#x2F;&#x2F;docs.python.org&#x2F;3.12&#x2F;library&#x2F;itertools.html#itertools.batched" rel="nofollow noreferrer">https:&#x2F;&#x2F;docs.python.org&#x2F;3.12&#x2F;library&#x2F;itertools.html#itertool...</a>

## 37740297 – philshem

Yes. I’ve written explicit code that needed this 100s of times.

## 37741068 – kastden

This is the greatest addition since f-strings!

## 37742836 – kzrdude

Great call-out! (Mistakes elided..)

## 37743193 – intalentive

Yeah I&#x27;ve memorized it by now:<p>for i in range(len(lst) &#x2F;&#x2F; batch_size + 1):
    batch = lst[i * batch_size : (i + 1) * batch_size]

## 37743832 – zem

yeah! that&#x27;s been in the ruby stdlib practically from day one, no idea why python was so resistant to it.

## 37749075 – hddqsb

You have a minor bug -- when len(lst) is a multiple of batch_size, this will have an extra iteration at the end with an empty batch. The fixed version is `range((len(lst) + batch_size - 1) &#x2F;&#x2F; batch_size)`, which emulates `ceil(len(lst) &#x2F; batch_size)`. Yet more proof that this should be part of stdlib :)<p>Personally I think I&#x27;d actually write it like this:<p><pre><code>    for i in range(0, len(lst), batch_size):
        batch = lst[i:i+batch_size]
</code></pre>
The docs give another pretty nice implementation using iter() and islice() in a loop (but it uses the walrus operator `:=` so it requires Python 3.8+ as written).

## 37750118 – rossant

Blatant reason why a native solution was long overdue.

## 37754712 – ehsankia

99% of my more_itertools imports are exactly for this.<p>there&#x27;s 1-2 other stuff from more_itertools that I think should make it to itertools. I&#x27;d actually like to see statistics from huge monorepos&#x2F;opensource about usage stats of various more_itertools functions.

## 37757788 – miiiiiike

Same but for the ‘batch’, ‘ibatch’, and ‘abatch’ functions I started writing back in 2008.

## 37762840 – abyesilyurt

Checkout more-itertools for more variants: <a href="https:&#x2F;&#x2F;pypi.org&#x2F;project&#x2F;more-itertools&#x2F;" rel="nofollow noreferrer">https:&#x2F;&#x2F;pypi.org&#x2F;project&#x2F;more-itertools&#x2F;</a>

