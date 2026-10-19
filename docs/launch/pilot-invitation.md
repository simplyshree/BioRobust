# BioRobust pilot invitation

## Primary message

I am building BioRobust, a free and open-source local tool that helps researchers and maintainers understand unfamiliar biological and scientific software repositories before running, reusing, or extending them.

BioRobust scans a local repository (or a public Git URL) without executing the repository code and produces Markdown, PDF, HTML, or JSON reports. The reports show observable evidence, uncertainty, limitations, and practical next steps. Repository contents are not sent to an online AI service by BioRobust.

I would love feedback from people working with genomics, bioinformatics, transcriptomics, proteomics, metabolomics, synthetic biology, neuroscience, biological imaging, ecology, systems biology, or other open-source research software.

Try it on a repository you know well:

```powershell
python -m pip install "biorobust @ git+https://github.com/simplyshree/BioRobust.git@v0.4.1"
biorobust start https://github.com/OWNER/PROJECT.git --format pdf --theme scientific --detail standard --output biorobust-report.pdf
```

Or scan a repository you already cloned:

```powershell
biorobust start . --format markdown --output biorobust-report.md
```

Please tell me:

1. Was the automatically selected profile appropriate?
2. Which findings or evidence were genuinely useful?
3. Which findings were false positives, unclear, or missing?
4. Did the report help you decide what to inspect or reproduce next?
5. Which biological or scientific repository type should BioRobust support better?

Please do not upload private or protected source code. A public repository link and a short description of what BioRobust got right or wrong are enough. This is a static triage and understanding aid, not scientific, clinical, security, or reproducibility certification.

Feedback and pilot reports can be shared through the [BioRobust issue tracker](https://github.com/simplyshree/BioRobust/issues).

## Short version

I am looking for pilot users for BioRobust, a free local-first tool for understanding open-source biological and scientific software repositories. It scans a clone or public Git URL without executing repository code and creates evidence-backed Markdown, PDF, HTML, or JSON reports.

Try it on a repository in your field and let me know: was the profile right, which findings helped, what was a false positive, and what evidence was missing? Please share only public repositories. Feedback: https://github.com/simplyshree/BioRobust/issues

## Suggested hashtags

`#OpenSource #ResearchSoftware #Bioinformatics #ComputationalBiology #Reproducibility #ScientificSoftware #SoftwareSustainability #LifeSciences`
