# Grading Procedure

An overall sheet of student id, basic information of datasets and technologies and the assignment file is given, e.g.:


|studentid|infrastructures|programming languages|data|messaging systems|databases|1st evaluation|2nd evaluation| lead teacher review
---|----|----|----|----|-----|---|--|--|
|1234   |container   | Python   |NY Taxi|Kafka  | Cassandra  | ABC  | ABC |ABC

Generally, the evaluator only knows the student id.
> Evaluators are TA and teachers.

The first round of assignment evaluation is based on the following steps:

1. an evaluator claims an open assignment by putting the evaluator name into "evaluators" in the overall sheet.
2. the evaluator downloads the zip file of the assignment to the machine used to evaluate the assignment
2. the evaluator unzips the file
3. the evaluator copies the template assignment[1,2,3]-grade-studentid.md into the assignment directory and modify the student id
    - the student id can bee seen in the zip file: "assignment[1,2,3]-studentid"
    - if we cannot see the studentid, then pls. check the source of the zipfile to see studentid in submitter.csv
    - if not, then pls assign a number and keep the name of the zip file clearly so we can trace
4. the evaluator grades and updates the assignment[1,2,3]-grade-studentid.md
   - follow the protocol of grading for individual assignment (within a grading team and cross grading teams)
     - discuss with team members
     - share common issues
     - if needed, a face-to-face meeting with students
     - etc.
   - check also selfgrading.csv to see selfgrading from students
   - some students do not do selfgrade (or just put a random grade)
5. The evaluator upload the assignment[1,2,3]-grade-studentid.md  report to the "done" directory
   - keep sources/tests in the evaluator's computer for final check, we will delete only after the final grade submitted.
6. The evaluator updates the overall sheet with basic information of datasets and technologies

After the first round, the second round of cross-team evaluation:

   * another evaluator selects an assignment and its evaluation report to perform the second round review to give comments/feedback to the first evaluator
      - also focus on detecting possible violation of the assignment
   * based on comments/feedback, the assessment will be revised

Final meta review from the head teacher:
   * the head teacher reviews assignments and its evaluation report and provide comments/feedback
   * the evaluation report will be revised

Reports will be sent to students. Students might be asked to come to explain after the report release as well as students can come to debate about student's grades.

Any change of grades will be performed and documented:
> the new/revised grade will be stored in a new directory, e.g., *new-done*, *new-new-done*. Previous grade reports will never be changed, only copy the previous report and modify the copied version.
