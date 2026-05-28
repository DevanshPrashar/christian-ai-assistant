# Approach Diagram - Chat Processing Flow

```mermaid
flowchart TD
    Start([👤 User Message]) --> In_Check

    subgraph InLayer["📥 Input Processing"]
        In_Check{Off-Topic<br/>Check?}
        In_Check -->|Yes| In_Deny["Redirect to<br/>Christian Topics"]
        In_Check -->|No| Tricky{Adversarial<br/>Prompt?}
    end

    subgraph SafetyLayer["🚫 Safety Checks"]
        Tricky -->|Weaponized<br/>Scripture| Wpn["Handle Weaponized<br/>Scripture"]
        Tricky -->|Adversarial<br/>Ignore| Adv["Handle Adversarial<br/>Prompt"]
        Tricky -->|Heretical| Her["Handle Heretical<br/>Content"]
        Tricky -->|Safe| Mod{Moderation<br/>Check?}
    end

    subgraph ModLayer["🛡️ Moderation"]
        Mod -->|Flagged| Mod_Deny["Return Denial<br/>Message"]
        Mod -->|Clean| Retrieve["Retrieve from<br/>Bible DB"]
    end

    subgraph RAGLayer["📖 RAG Pipeline"]
        Retrieve -->|Search| Search["Find Relevant<br/>Verses"]
        Search -->|Top 5| Context["Build Context<br/>with Verses"]
        Context -->|Inject| LLM_Call["Call MiniMax<br/>LLM"]
    end

    subgraph LLMProc["🤖 LLM Processing"]
        LLM_Call --> LLM_Resp
        LLM_Resp{Valid<br/>Response?}
        LLM_Resp -->|Corrupted| Retry{Retry<br/>< 3?}
        Retry -->|Yes| LLM_Call
        Retry -->|No| Err["Return Error<br/>Message"]
        LLM_Resp -->|Yes| Out_Proc
    end

    subgraph OutLayer["📤 Output Processing"]
        Out_Proc["Check Output<br/>Moderation"]
        Out_Proc --> Fake{Fake<br/>Verses?}
        Fake -->|Yes| Warn["Add Warning<br/>about Fake Verses"]
        Fake -->|No| Extract["Extract Verse<br/>References"]
        Warn --> Extract
        Extract --> Save["Save to<br/>Conversation"]
        Save --> End([✅ Return<br/>Response])
    end

    %% Denial paths all go to Save
    In_Deny --> Save
    Wpn --> Save
    Adv --> Save
    Her --> Save
    Mod_Deny --> Save

    %% Styling
    style Start fill:#4CAF50,color:#fff
    style End fill:#4CAF50,color:#fff
    style In_Check fill:#FF9800
    style Tricky fill:#f44336,color:#fff
    style Mod fill:#FF9800
    style RAGLayer fill:#2196F3,color:#fff
    style LLMProc fill:#9C27B0,color:#fff
    style OutLayer fill:#2196F3,color:#fff
```

---

## Step-by-Step Flow

### 1. Input Reception
```
User sends message → API receives → Check if off-topic
```

### 2. Safety Checks (Early Exit)
```
Off-topic? → Redirect (exit)
Adversarial prompt? → Deny (exit)
Heretical content? → Deny (exit)
Moderation flagged? → Deny (exit)
```

### 3. RAG Pipeline
```
Retrieve → Keyword search Bible DB → Get top 5 verses
                                      ↓
Build context → Inject verses into prompt
                                      ↓
Call MiniMax LLM → Get response
```

### 4. Validation & Retry
```
Response valid? → No → Retry (max 3 attempts)
Response valid? → Yes → Continue
```

### 5. Output Processing
```
Output moderation check
       ↓
Fake verse detection
       ↓
Extract verse references
       ↓
Save to conversation history
       ↓
Return response
```

---

## Image Generation Flow

```mermaid
flowchart LR
    Start2([🖼️ Image Request]) --> ImgPrompt["User's Image<br/>Prompt"]
    ImgPrompt --> SafeCheck{Safety<br/>Check?}
    SafeCheck -->|Blocked| Blocked["Return Blocked<br/>Error"]
    SafeCheck -->|Safe| Prefix["Add Christian<br/>Prefix"]
    Prefix --> MiniMaxImg["Call MiniMax<br/>Image API"]
    MiniMaxImg -->|Success| ImgURL["Return<br/>Image URL"]
    MiniMaxImg -->|Fail| Dalle["Fallback to<br/>DALL-E 3"]
    Dalle --> DalleURL["Return<br/>Image URL"]
    ImgURL --> End2([✅ Image URL])
    DalleURL --> End2
    Blocked --> End2

    style Start2 fill:#4CAF50,color:#fff
    style End2 fill:#4CAF50,color:#fff
    style SafeCheck fill:#FF9800
    style MiniMaxImg fill:#2196F3,color:#fff
    style Dalle fill:#9C27B0,color:#fff
```
