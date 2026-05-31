.PHONY: all book.pdf clean

INPUTS = metadata.yaml \
         foreword.md \
         manuscript/preface.md \
         manuscript/ch01.md \
         manuscript/ch02.md \
         manuscript/ch03.md \
         manuscript/ch04.md \
         manuscript/ch05.md \
         manuscript/conclusion.md \
         manuscript/appendix-a.md \
         manuscript/bibliography.md

CSL    = manuscript/chicago-fullnote-bibliography.csl
OUTPUT = book.pdf

all: $(OUTPUT)

$(OUTPUT): $(INPUTS) $(CSL)
	pandoc $(INPUTS) \
		--pdf-engine=xelatex \
		--citeproc \
		--csl=$(CSL) \
		--output=$(OUTPUT)

epub: $(INPUTS) $(CSL)
	pandoc $(INPUTS) \
		--citeproc \
		--csl=$(CSL) \
		--output=book.epub

html: $(INPUTS) $(CSL)
	pandoc $(INPUTS) \
		--citeproc \
		--csl=$(CSL) \
		--self-contained \
		--output=book.html

clean:
	rm -f $(OUTPUT) book.epub book.html

# Neuro-Somatic Archive targets
NSA_INPUTS = neuro-somatic-archive/ARCHITECTURE.md \
             neuro-somatic-archive/MASTER_INDEX.md \
             neuro-somatic-archive/BIOLOGICAL_BILL_OF_RIGHTS.md \
             neuro-somatic-archive/glossary.md \
             neuro-somatic-archive/modules/01_Neurodevelopmental.md \
             neuro-somatic-archive/modules/02_Schizophrenia.md \
             neuro-somatic-archive/modules/03_Bipolar.md \
             neuro-somatic-archive/modules/04_Depressive.md \
             neuro-somatic-archive/modules/05_Anxiety.md \
             neuro-somatic-archive/modules/06_OCD.md \
             neuro-somatic-archive/modules/07_Trauma.md \
             neuro-somatic-archive/modules/08_Dissociative.md \
             neuro-somatic-archive/modules/09_Somatic.md \
             neuro-somatic-archive/modules/10_Feeding_Eating.md \
             neuro-somatic-archive/modules/11_Elimination.md \
             neuro-somatic-archive/modules/12_Sleep_Wake.md \
             neuro-somatic-archive/modules/13_Sexual.md \
             neuro-somatic-archive/modules/14_Gender_Incongruence.md \
             neuro-somatic-archive/modules/15_Disruptive_Impulse_Conduct.md \
             neuro-somatic-archive/modules/16_Substance_Addictive.md \
             neuro-somatic-archive/modules/17_Neurocognitive.md \
             neuro-somatic-archive/modules/18_Personality.md \
             neuro-somatic-archive/modules/19_Paraphilic.md \
             neuro-somatic-archive/modules/20_Other.md

nsa-pdf: $(NSA_INPUTS)
	pandoc $(NSA_INPUTS) \
		--pdf-engine=xelatex \
		--output=neuro-somatic-archive.pdf

nsa-epub: $(NSA_INPUTS)
	pandoc $(NSA_INPUTS) \
		--output=neuro-somatic-archive.epub

nsa-html: $(NSA_INPUTS)
	pandoc $(NSA_INPUTS) \
		--self-contained \
		--output=neuro-somatic-archive.html
