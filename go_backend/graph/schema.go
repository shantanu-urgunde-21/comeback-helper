package graph

type MathEntityType string

const (
	Axiom      MathEntityType = "Axiom"
	Definition MathEntityType = "Definition"
	Lemma      MathEntityType = "Lemma"
	Theorem    MathEntityType = "Theorem"
	Corollary  MathEntityType = "Corollary"
	Proof      MathEntityType = "Proof"
	Formula    MathEntityType = "Formula"
	Example    MathEntityType = "Example"
	Concept    MathEntityType = "Concept"
)

type MathRelationType string

const (
	UsesAxiom       MathRelationType = "USES_AXIOM"
	UsesDefinition  MathRelationType = "USES_DEFINITION"
	UsesLemma       MathRelationType = "USES_LEMMA"
	Proves          MathRelationType = "PROVES"
	CorollaryOf     MathRelationType = "COROLLARY_OF"
	PrerequisiteFor MathRelationType = "PREREQUISITE_FOR"
	DependsOn       MathRelationType = "DEPENDS_ON"
	Contains        MathRelationType = "CONTAINS"
)

type Provenance struct {
	DocID          string `json:"doc_id"`
	DocTitle       string `json:"doc_title"`
	DocPath        string `json:"doc_path,omitempty"`
	PageNumber     int    `json:"page_number,omitempty"`
	SectionHeading string `json:"section_heading,omitempty"`
	ExactQuote     string `json:"exact_quote,omitempty"`
}

type ConceptTaxonomy struct {
	Domain    string `json:"domain"`
	Subdomain string `json:"subdomain"`
	Topic     string `json:"topic"`
}

type GraphNode struct {
	ID          string          `json:"id"`
	Name        string          `json:"name"`
	EntityType  MathEntityType  `json:"entity_type"`
	Taxonomy    ConceptTaxonomy `json:"taxonomy"`
	Aliases     []string        `json:"aliases,omitempty"`
	Description string          `json:"description"`
	Provenance  []Provenance    `json:"provenance,omitempty"`
}

type GraphEdge struct {
	Source      string           `json:"source"`
	Target      string           `json:"target"`
	Relation    MathRelationType `json:"relation"`
	Description string           `json:"description,omitempty"`
	Provenance  []Provenance     `json:"provenance,omitempty"`
}

type MathEntityExtraction struct {
	Nodes []GraphNode `json:"nodes"`
	Edges []GraphEdge `json:"edges"`
}
