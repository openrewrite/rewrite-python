plugins {
    id("org.openrewrite.build.language-library")
}

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

tasks.compileJava {
    options.release = 8
}

// disable all tests temporarily
tasks.withType<Test> {
    // This disables all test tasks
    isEnabled = false
}

dependencies {

    compileOnly("com.google.auto.service:auto-service-annotations:1.1.1")
    annotationProcessor("com.google.auto.service:auto-service:1.1.1")

    implementation("org.openrewrite:rewrite-remote:$latest") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }
    implementation(project(":rewrite-python"))

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")
}