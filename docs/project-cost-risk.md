# ReplayLab Cost and Billing Risk

Last checked: May 4, 2026.

## Short Answer

ReplayLab can likely be built with **$0 out-of-pocket** if we stay within free credits/free tiers and avoid paid upgrades.

The main cost risk is not the project idea itself. The main risk is accidentally leaving paid GPU/cloud resources running or enabling paid subscriptions.

## Likely Free / Included

- AMD AI Developer Program is free to join for approved developers.
- The hackathon advertises **$100 AMD Developer Cloud credits** for eligible AMD AI Developer Program members.
- The hackathon includes access to AMD Instinct MI300X GPUs through AMD Developer Cloud.
- Hugging Face Spaces CPU Basic can be used free for a lightweight app/demo UI.
- GitHub public repositories are free.
- Open-source models can avoid paid API usage.
- The hackathon brief mentions a 1-month complimentary DeepLearning.AI Pro membership.

## Where Money Could Be Charged

## AMD Developer Cloud

- Pay-as-you-go access may require payment information.
- If a payment method is attached, charges may occur after credits are exhausted.
- Powered-off GPU VMs may still bill because disk, CPU, RAM, and IP resources remain reserved.
- Charges continue until the instance is destroyed.
- Complimentary credits may apply only to AMD Instinct MI300X GPU usage, not necessarily attached volumes, object storage, or backups.
- Credits may expire, so unused credit is not permanent.

## Hugging Face

- CPU Basic Spaces are free.
- GPU Spaces are paid by the minute/hour if upgraded.
- Paid GPU Spaces can continue running unless paused or downgraded.
- Hugging Face Pro is optional and currently listed at $9/month.

## DeepLearning.AI

- The hackathon mentions a complimentary 1-month Pro membership.
- DeepLearning.AI Pro is a paid subscription outside the complimentary period.
- If a trial or subscription asks for payment details, cancel before renewal if we do not want charges.

## Third-Party APIs

- Paid LLM APIs are not required for ReplayLab.
- Use local/open-source models where possible.
- If using OpenAI/Anthropic/etc., set hard spend limits first.

## Recommended No-Surprise-Cost Plan

1. Use AMD Developer Cloud only after credits are confirmed.
2. Use the smallest viable AMD GPU instance.
3. Destroy GPU instances immediately after each work session.
4. Do not rely on "power off" as a cost-saving action.
5. Avoid extra volumes, backups, object storage, or paid persistent services unless truly needed.
6. Keep Hugging Face Space on CPU Basic for the UI.
7. Run real GPU experiments on AMD Cloud, then display captured results through the app.
8. Avoid Hugging Face GPU Spaces unless we have a grant or explicit budget.
9. Avoid paid LLM APIs unless a strict budget cap is configured.
10. Set calendar reminders for any complimentary trial or subscription renewal.

## Practical Budget Target

- **Target:** $0 out-of-pocket.
- **Safe buffer:** $0-$10 only if a small paid API or hosting feature becomes unavoidable.
- **Avoid:** Any GPU resource that bills after credits are exhausted.

## Cost Decision

We should design ReplayLab so the demo requires AMD GPU compute only for the captured experiment run, not for always-on hosting.

Best architecture for cost control:

- AMD Developer Cloud: run GPU experiment, collect telemetry, produce replay evidence.
- Hugging Face Space CPU Basic or local app: show UI, timeline, logs, and demo narrative.
- GitHub: host code and artifacts.

## Sources Checked

- AMD AI Developer Program: https://www.amd.com/en/developer/ai-dev-program.html
- AMD Developer Cloud: https://www.amd.com/en/developer/resources/cloud-access/amd-developer-cloud.html
- AMD Developer Hackathon on lablab.ai: https://lablab.ai/ai-hackathons/amd-developer
- Hugging Face Spaces docs: https://huggingface.co/docs/hub/spaces-overview
- Hugging Face pricing: https://huggingface.co/pricing
- DeepLearning.AI membership: https://learn.deeplearning.ai/membership
