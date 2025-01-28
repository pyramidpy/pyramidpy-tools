from typing import List, Optional

import numpy as np
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas import EvaluationDataset, evaluate
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import FactualCorrectness, Faithfulness, LLMContextRecall


class RAG:
    def __init__(self, model="gpt-4o", api_key=None):
        self.llm = ChatOpenAI(model=model, api_key=api_key)
        self.embeddings = OpenAIEmbeddings(api_key=api_key)
        self.doc_embeddings = None
        self.docs = None

    def load_documents(self, documents):
        """Load documents and compute their embeddings."""
        self.docs = documents
        self.doc_embeddings = self.embeddings.embed_documents(documents)

    def get_most_relevant_docs(self, query):
        """Find the most relevant document for a given query."""
        if not self.docs or not self.doc_embeddings:
            raise ValueError("Documents and their embeddings are not loaded.")

        query_embedding = self.embeddings.embed_query(query)
        similarities = [
            np.dot(query_embedding, doc_emb)
            / (np.linalg.norm(query_embedding) * np.linalg.norm(doc_emb))
            for doc_emb in self.doc_embeddings
        ]
        most_relevant_doc_index = np.argmax(similarities)
        return [self.docs[most_relevant_doc_index]]

    def generate_answer(self, query, relevant_doc):
        """Generate an answer for a given query based on the most relevant document."""
        prompt = f"question: {query}\n\nDocuments: {relevant_doc}"
        messages = [
            (
                "system",
                "You are a helpful assistant that answers questions based on given documents only.",
            ),
            ("human", prompt),
        ]
        ai_msg = self.llm.invoke(messages)
        return ai_msg.content


def eval_rag(
    rag: RAG,
    sample_queries: List[str],
    expected_responses: List[str],
    api_key: Optional[str] = None,
    evaluator_llm: Optional[str] = "gpt-4o-mini",
) -> dict:
    rag = RAG(api_key=api_key)
    dataset = []

    for query, reference in zip(sample_queries, expected_responses):
        relevant_docs = rag.get_most_relevant_docs(query)
        response = rag.generate_answer(query, relevant_docs)
        dataset.append(
            {
                "user_input": query,
                "retrieved_contexts": relevant_docs,
                "response": response,
                "reference": reference,
            }
        )
    llm = ChatOpenAI(model=evaluator_llm)
    evaluation_dataset = EvaluationDataset.from_list(dataset)
    evaluator_llm = LangchainLLMWrapper(llm)

    result = evaluate(
        dataset=evaluation_dataset,
        metrics=[LLMContextRecall(), Faithfulness(), FactualCorrectness()],
        llm=evaluator_llm,
    )
    return result
