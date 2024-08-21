plugins {
    id("org.openrewrite.build.language-library") version "latest.integration"
    id("nebula.release") version "17.1.0"
}
group = "org.openrewrite"
description = "Rewrite Python"

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

dependencies {
    compileOnly("org.openrewrite:rewrite-test")
    compileOnly("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")

    testRuntimeOnly("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }
}
