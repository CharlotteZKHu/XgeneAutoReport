import subprocess, sys

tex = "generated_reports/Report_Jane_Doe.tex"
cmd = ["pdflatex", "-interaction=nonstopmode", tex]

for i in range(3):   # 2 runs usually enough; 3rd is safe
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    print(f"Run {i+1} exit {r.returncode}")
    if r.returncode != 0:
        print(r.stdout)
        sys.exit(r.returncode)
# done
