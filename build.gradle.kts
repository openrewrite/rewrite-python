plugins {
    id("org.openrewrite.build.recipe-library") version "latest.release"
}

group = "org.openrewrite"
description = "Rewrite Python"

val latest = if (project.hasProperty("releasing")) {
    "latest.release"
} else {
    "latest.integration"
}

// disable all tests temporarily
tasks.withType<Test> {
    // This disables all test tasks
    isEnabled = false
}

dependencies {
    compileOnly("org.openrewrite:rewrite-test")
    implementation("org.openrewrite:rewrite-remote-java:latest.integration") {
        exclude(group = "org.openrewrite", module = "rewrite-python")
    }

    implementation(platform("org.openrewrite:rewrite-bom:$latest"))
    implementation("org.openrewrite:rewrite-core")
    implementation("org.openrewrite:rewrite-java")

    testImplementation("org.openrewrite:rewrite-test")
    testImplementation("org.junit-pioneer:junit-pioneer:latest.release")
}

val poetryProjectDir = file("rewrite")
val outputDir = layout.buildDirectory.dir("resources/main/META-INF")
val requirementsFile = outputDir.map { it.file("python-requirements.txt") }

tasks.register("prepareOutputDir") {
    doLast {
        outputDir.get().asFile.mkdirs()
    }
}

tasks.register<Exec>("exportPoetryRequirements") {
    dependsOn("prepareOutputDir")
    workingDir = poetryProjectDir
    commandLine("sh", "-c", "poetry export --without-hashes -o ${requirementsFile.get().asFile.absolutePath}")
}

tasks.register("appendOpenRewriteRequirements") {
    dependsOn("exportPoetryRequirements")
    doLast {
        val file = requirementsFile.get().asFile
        file.appendText("\ncbor2\nopenrewrite\nopenrewrite-remote\n")
    }
}

tasks.named("processResources") {
    dependsOn("appendOpenRewriteRequirements")
}