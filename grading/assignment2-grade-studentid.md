# IMPORTANT NOTE

This grade is provisional. Why: we need to cross-check all assignments and maybe a face-to-face question to finalize the grade. We also do check the assignments w.r.t. the rule after releasing this grade. In principle, the final grade will be fixed at the end of the course. If you have any feedback, you can send it.

----------------

Overall Grade:
Overall comments:

Requests for face-to-face explanation:

-----------------
Part 1 (weighted factor=3, max 15 points):

Point 1.1

A set of constraints for files to be ingested:

A set of constraints for the tenant service profile:

Explain such constraints:

Implement these constraints (configurable/flexible) and examples:


Point 1.2

Explain the design of **clientbatchingestapp**  - the flow/interface/architecture/technologies:

Explain the design of **clientbatchingestapp**  - internal logic/ingestion/data wrangling:


Provide one implementation - the internal logic/data wrangling:

Provide one implementation - the input/output, execution model:

Point 1.3

Design  **mysimbdp-batchingestmanager** - the flow/interface/architecture/technologies:

Design **mysimbdp-batchingestmanager** - support multiple apps/tenants/integration models with apps:


Implement **mysimbdp-batchingestmanager** (especially how does it support "blackbox" apps):

Explain **mysimbdp-batchingestmanager** schedules:


Point 1.4

Explain the multi-tenancy  model in **mysimbdp**:

Develop test programs (**clientbatchingestapp**):

Develop test data and test profiles for tenants (min 2 different tenants):

Show the performance of ingestion tests (min 2 different tenants):


Point 1.5

Explain logging features w.r.t. metrics, successful/failed operations:

Explain how logging information stored in separate files/databases, etc.:

Implement the logging features:

Provide and explain statistical data extracted from logs  for individual tenants/whole system:


Part 2 (weighted factor=3, max 15 points):


Point 2.1:

Explain the multi-tenancy model - shared/dedicated parts:

Explain the multi-tenancy model - the logic/correctness:

Design set of constraints for the tenant service profile:

Explain constraints:

Point 2.2

Design **mysimbdp-streamingestmanager** - features:

Design **mysimbdp-streamingestmanager** - integration/execution models for  apps (for multitenant, configuration, ...):

Implement **mysimbdp-streamingestmanager** - features:

Implement  **mysimbdp-streamingestmanager** - integration/execution models (configuration/tightly vs loosely coupling):


Point 2.3.

Develop test ingestion programs (**clientstreamingestapp**):

Develop test data, and test profiles for tenants:

Perform ingestion tests (min 2 tenants):

Explain tests:

Point 2.4.

Design metrics to be reported/collected:

Explain metrics and reporting mechanism:

Design the report format:

Explain possible components/flows for reporting:


Point 2.5.

Implement the feature in **mysimbdp-streamingestmonitor**:


Design the notification mechanism - constraints/when:

Design the notification structure informing about the situation:

Implementation the feature to receive the notification in **mysimbdp-streamingestmanager**:


Part 3 (weighted factor=1, max 5 points):


Point 3.1.

Present an architecture for the logging and monitoring of both batch and near-realtime ingestion features:

Explain the architecture:

Point 3.2:

Explain choices/examples of different sinks:

Explain recommendations to the tenants:

Point 3.3:

Explain assumed protections for tenants:

Provide recommendations for tenants:


Point 3.4:

Explain features for detecting quality of data:

Explain how the provider and the tenant can work together:

Point 3.5:

Explain the implication of types of daa and workloads:

Explain the extension:
