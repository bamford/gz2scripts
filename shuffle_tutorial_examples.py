import numpy as N

def shuffle(nmax=15, nrow=5):
    f = file('../data/tutorial_examples_selected')
    lines = f.readlines()
    outlines = []
    examples = []
    q = 0
    lines.append('=== Q: END')
    for l in lines:
        if l.startswith('=== Q'):
            if len(examples) > 0:
                ne = len(examples)
                thisnmax = min(nrow*(ne/nrow), nmax)
                r = []
                while len(r) < thisnmax:
                    newr = int(N.random.uniform(0, ne))
                    if newr not in r:
                        r.append(newr)
                a = 0
                for e in [examples[i] for i in r]:
                    a += 1
                    if a==6:
                        outlines.append('  </tr><tr>\n')
                    outlines.append(html_format(e, q, a))
            current_answer = None
            examples = []
            outlines.append('\n'+l)
            q += 1
        if l.startswith('==== A'):
            current_answer = l[8:-6]
        if l.startswith('http'):
            examples.append([l[:-6], current_answer])
    outf = file('../data/tutorial_examples_html', 'w')
    outf.writelines(outlines)
    outf.close()

        
def html_format(e, q, a):
    url, text = e
    info = {'url':url, 'text':text, 'q':q, 'a':a, 'percent':'%'}
    format = '''    <td width="20%(percent)s" align="center" valign="top">
    <div class="example_wrap">
      <img src="%(url)s"
           onclick="showAnswer(\'answer_%(q)i_%(a)i\')"
	   onmouseout="hideAnswer('answer_%(q)i_%(a)i')" />
    <div class="example_answer" id="answer_%(q)i_%(a)i">%(text)s</div>
    </div>
    </td>
'''
    return format%info
