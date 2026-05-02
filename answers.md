# Writeup

## Q1. What problems existed in the original lab system?

The original lab system had several limitations that made it unsuitable for real-world use. Models were stored only on the local machine, which made them difficult to share and vulnerable to loss if the system failed. There was no model versioning, so updates could overwrite previous models without any tracking or rollback capability. Additionally, the system lacked automation and orchestration, meaning training, evaluation, and deployment had to be done manually, increasing the risk of human error and inconsistency.

---

## Q2. Why is storing models locally dangerous in production systems?

Storing models locally is risky because local machines are not reliable or scalable in production environments. If the machine crashes, is replaced, or loses data, the model is permanently lost. Local storage also prevents other services or systems from accessing the model, making it difficult to scale applications or support distributed systems. In production, centralized storage solutions like S3 are preferred because they provide durability, availability, and easy access across multiple components.

---

## Q3. Why do we add evaluation before promoting a model?

Evaluation is a critical step before promoting a model because it ensures that the model performs well on unseen data. Without evaluation, a poorly performing or broken model could be deployed, leading to incorrect predictions and negative business impact. By measuring metrics such as accuracy, we can verify that the new model meets a defined performance threshold. This step also allows comparison with previous versions, ensuring that only improved or acceptable models are promoted to production.

---

## Q4. Why do we need model versioning?

Model versioning is important because it allows teams to track changes and manage multiple versions of models over time. Each version can be linked to specific data, parameters, and training conditions, making experiments reproducible. It also provides the ability to roll back to a previous stable version if a newly deployed model causes issues. Without versioning, managing models becomes chaotic, especially as the number of experiments and deployments increases.

---

## Q5. Why might managing models manually become difficult as the number of models grows?

As the number of models increases, manual management becomes inefficient and error-prone. Tracking which model is deployed, which version performed best, and where each model is stored becomes increasingly complex. There is a higher risk of deploying the wrong model or losing important information about previous experiments. To handle this complexity, automation tools like Airflow and structured storage systems like S3 are used to manage model pipelines, ensuring consistency, scalability, and reliability.