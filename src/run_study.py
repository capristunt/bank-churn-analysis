"""Exécuter en kernels IPython neufs : .venv/bin/python src/run_study.py [01|02|03|04|summary].

Un processus Python isolé et un InProcessKernel neuf par notebook évitent les
sockets interdits par certains sandboxes. Aucun état Python n'est partagé.
"""
from pathlib import Path
import os
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

def execute(path):
    import nbformat
    from IPython.utils.capture import capture_output
    from ipykernel.inprocess.manager import InProcessKernelManager
    nb = nbformat.read(path, as_version=4)
    os.chdir(ROOT / 'notebooks')
    km = InProcessKernelManager()
    km.start_kernel()
    shell = km.kernel.shell
    shell.run_line_magic('matplotlib', 'inline')
    count = 0
    try:
        for cell in nb.cells:
            if cell.cell_type != 'code':
                continue
            count += 1
            with capture_output() as captured:
                result = shell.run_cell(cell.source, store_history=True)
            if not result.success:
                raise RuntimeError(f'{path.name}, cellule {count}: {result.error_before_exec or result.error_in_exec}')
            outputs = []
            if captured.stdout:
                outputs.append(nbformat.v4.new_output('stream', name='stdout', text=captured.stdout))
            if captured.stderr:
                outputs.append(nbformat.v4.new_output('stream', name='stderr', text=captured.stderr))
            for out in captured.outputs:
                outputs.append(nbformat.v4.new_output('display_data', data=out.data, metadata=out.metadata))
            cell.outputs = outputs
            cell.execution_count = count
        nbformat.write(nb, path)
    finally:
        km.shutdown_kernel()

if __name__ == '__main__':
    if len(sys.argv) == 3 and sys.argv[1] == '--worker':
        execute(Path(sys.argv[2]))
    else:
        paths = sorted((ROOT / 'notebooks').glob('[0-9][0-9]-*.ipynb'))
        if len(sys.argv) > 1:
            if sys.argv[1] == 'summary':
                paths = [ROOT / 'notebooks/bank-churn-summary.ipynb']
            else:
                paths = [p for p in paths if p.name.startswith(sys.argv[1] + '-')]
        assert paths, 'Aucun notebook sélectionné'
        for path in paths:
            print(f'Exécution kernel neuf : {path.name}', flush=True)
            with tempfile.TemporaryDirectory(prefix='churn-ipython-') as tmp:
                env = dict(os.environ, IPYTHONDIR=tmp, MPLCONFIGDIR=tmp)
                subprocess.run([sys.executable, __file__, '--worker', str(path)], env=env, check=True)
            print(f'Terminé : {path.name}', flush=True)
